from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # ── YouTube ──────────────────────────────────────────────────────────────
    youtube_api_key: str = ""
    youtube_categories: str = "25,27,28"
    youtube_region: str = "TR"
    videos_per_category: int = 10
    comments_per_video: int = 100

    # ── LLM ─────────────────────────────────────────────────────────────────
    # Desteklenen değerler: "claude" | "gemini" | "chatgpt"
    llm_provider: Literal["claude", "gemini", "chatgpt"] = "chatgpt"

    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    chatgpt_api_key: str = ""           # CHATGPT_API_KEY → buraya map'lenir
    chatgpt_model: str = "gpt-4o-mini"  # gpt-4o-mini: ucuz + hızlı; gpt-4o da olur

    sentiment_batch_size: int = 20
    llm_max_tokens: int = 2048

    # ── Paths ────────────────────────────────────────────────────────────────
    raw_data_dir: Path = Path("raw_data")
    processed_data_dir: Path = Path("processed_data")

    class Config:
        env_file = ".env"
        # .env'deki CHATGPT_API_KEY → chatgpt_api_key alanına otomatik bağlanır

    @property
    def category_ids(self) -> list[str]:
        return [c.strip() for c in self.youtube_categories.split(",")]

    def ensure_dirs(self) -> None:
        for d in [self.raw_data_dir, self.processed_data_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()


# ── Pydantic Models ───────────────────────────────────────────────────────────

class Comment(BaseModel):
    comment_id: str
    text: str
    author: str
    like_count: int = 0
    published_at: datetime


class VideoData(BaseModel):
    video_id: str
    title: str
    channel_name: str
    category_id: str
    category_name: str
    view_count: int
    like_count: int
    comment_count: int
    published_at: datetime
    thumbnail_url: str
    comments: list[Comment] = Field(default_factory=list)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class SentimentScore(BaseModel):
    anger: float = Field(ge=0, le=1)
    joy: float = Field(ge=0, le=1)
    trust: float = Field(ge=0, le=1)
    fear: float = Field(ge=0, le=1)
    surprise: float = Field(ge=0, le=1)
    sadness: float = Field(ge=0, le=1)
    disgust: float = Field(ge=0, le=1)
    anticipation: float = Field(ge=0, le=1)


class AnalyzedComment(BaseModel):
    comment_id: str
    text: str
    sentiment: SentimentScore
    dominant_emotion: str
    confidence: float


class VideoAnalysis(BaseModel):
    video_id: str
    title: str
    channel_name: str
    category_id: str
    category_name: str
    view_count: int
    like_count: int
    thumbnail_url: str
    total_comments_analyzed: int
    aggregate_sentiment: SentimentScore
    dominant_emotion: str
    sentiment_distribution: dict[str, int]
    analyzed_comments: list[AnalyzedComment]
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


CATEGORY_NAMES: dict[str, str] = {
    "25": "Haberler & Politika",
    "27": "Eğitim",
    "28": "Bilim & Teknoloji",
    "22": "İnsanlar & Bloglar",
    "24": "Eğlence",
    "17": "Spor",
    "10": "Müzik",
    "20": "Oyun",
}