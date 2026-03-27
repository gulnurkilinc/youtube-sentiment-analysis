from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "")

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_exponential

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings, VideoData, Comment, CATEGORY_NAMES

console = Console()


class YouTubeFetcher:

    def __init__(self, api_key: str):
        self.youtube = build(
            "youtube", "v3",
            developerKey=api_key,
            cache_discovery=False
        )
        self.quota_used = 0

    def get_trending_videos(self, category_id: str, region_code: str = "TR", max_results: int = 10) -> list[dict]:
        try:
            response = (
                self.youtube.videos()
                .list(
                    part="snippet,statistics",
                    chart="mostPopular",
                    regionCode=region_code,
                    videoCategoryId=category_id,
                    maxResults=max_results,
                )
                .execute()
            )
            self.quota_used += 1
            return response.get("items", [])
        except HttpError as e:
            logger.warning(f"Kategori {category_id} bulunamadı: {e}")
            return []

    def get_comments(self, video_id: str, max_results: int = 100) -> list[dict]:
        all_comments = []
        next_page_token = None

        while len(all_comments) < max_results:
            try:
                response = (
                    self.youtube.commentThreads()
                    .list(
                        part="snippet",
                        videoId=video_id,
                        order="relevance",
                        maxResults=min(100, max_results - len(all_comments)),
                        pageToken=next_page_token,
                        textFormat="plainText",
                    )
                    .execute()
                )
                self.quota_used += 1

                items = response.get("items", [])
                if not items:
                    break

                for item in items:
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    all_comments.append(snippet)

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            except HttpError as e:
                if e.resp.status == 403:
                    logger.warning(f"Video {video_id}: Yorumlar devre dışı.")
                    break
                raise

        return all_comments

    def parse_video(self, item: dict, category_id: str) -> VideoData | None:
        try:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            published_str = snippet.get("publishedAt", "")

            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            if published_at < cutoff:
                return None

            return VideoData(
                video_id=item["id"],
                title=snippet.get("title", ""),
                channel_name=snippet.get("channelTitle", ""),
                category_id=category_id,
                category_name=CATEGORY_NAMES.get(category_id, f"Kategori {category_id}"),
                view_count=int(stats.get("viewCount", 0)),
                like_count=int(stats.get("likeCount", 0)),
                comment_count=int(stats.get("commentCount", 0)),
                published_at=published_at,
                thumbnail_url=(
                    snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                ),
            )
        except Exception as e:
            logger.error(f"Video parse hatası: {e}")
            return None

    def parse_comments(self, raw_comments: list[dict]) -> list[Comment]:
        comments = []
        for i, snippet in enumerate(raw_comments):
            try:
                comments.append(
                    Comment(
                        comment_id=f"c_{i}_{snippet.get('videoId', '')}",
                        text=snippet.get("textDisplay", ""),
                        author=snippet.get("authorDisplayName", "Anonim"),
                        like_count=int(snippet.get("likeCount", 0)),
                        published_at=datetime.fromisoformat(
                            snippet["publishedAt"].replace("Z", "+00:00")
                        ),
                    )
                )
            except Exception as e:
                logger.debug(f"Yorum atlandı: {e}")
        return comments


def run_fetcher() -> Path:
    settings.ensure_dirs()

    fetcher = YouTubeFetcher(api_key=settings.youtube_api_key)
    all_videos: list[dict] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    console.rule("[bold blue]Agent 1: The Fetcher[/bold blue]")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console) as progress:
        task = progress.add_task("Kategoriler işleniyor...", total=len(settings.category_ids))

        for cat_id in settings.category_ids:
            cat_name = CATEGORY_NAMES.get(cat_id, cat_id)
            progress.update(task, description=f"[cyan]{cat_name}[/cyan] çekiliyor...")

            raw_videos = fetcher.get_trending_videos(
                category_id=cat_id,
                region_code=settings.youtube_region,
                max_results=settings.videos_per_category,
            )

            for raw_video in raw_videos:
                video = fetcher.parse_video(raw_video, cat_id)
                if video is None:
                    continue

                try:
                    raw_comments = fetcher.get_comments(
                        video_id=video.video_id,
                        max_results=settings.comments_per_video,
                    )
                    video.comments = fetcher.parse_comments(raw_comments)
                except Exception as e:
                    logger.warning(f"Yorum çekme başarısız {video.video_id}: {e}")

                all_videos.append(video.model_dump(mode="json"))

            progress.advance(task)

    output_path = settings.raw_data_dir / f"fetch_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "fetched_at": timestamp,
                    "total_videos": len(all_videos),
                    "total_comments": sum(len(v.get("comments", [])) for v in all_videos),
                },
                "videos": all_videos,
            },
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    table = Table(title="Fetcher Özeti")
    table.add_column("Metrik")
    table.add_column("Değer", justify="right")
    table.add_row("Toplam video", str(len(all_videos)))
    table.add_row("Toplam yorum", str(sum(len(v.get("comments", [])) for v in all_videos)))
    table.add_row("Çıktı", str(output_path))
    console.print(table)

    return output_path


if __name__ == "__main__":
    run_fetcher()