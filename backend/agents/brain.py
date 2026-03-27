from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

# ── Provider imports (graceful fallback) ─────────────────────────────────────
try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from tenacity import retry, stop_after_attempt, wait_exponential

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    settings,
    VideoData,
    VideoAnalysis,
    AnalyzedComment,
    SentimentScore,
)

console = Console()


# ── Shared prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Sen bir duygu analizi uzmanısın. Sana verilen yorumları analiz edecek ve her biri için 8 temel duygu skorunu (0.0 ile 1.0 arasında) belirleyeceksin.

8 Duygu Kategorisi:
- anger (öfke)
- joy (sevinç)
- trust (güven)
- fear (korku)
- surprise (sürpriz)
- sadness (üzüntü)
- disgust (iğrenme)
- anticipation (beklenti)

KURALLARI KESİNLİKLE UYGULA:
1. YALNIZCA ham JSON döndür. Başka hiçbir metin yazma.
2. Yanıtın ilk karakteri { olmalı, son karakteri } olmalı.
3. Kesinlikle ``` kullanma, açıklama yazma, özet yapma.

Yanıt formatı:
{
  "results": [
    {
      "comment_id": "...",
      "scores": {
        "anger": 0.0,
        "joy": 0.8,
        "trust": 0.6,
        "fear": 0.0,
        "surprise": 0.2,
        "sadness": 0.0,
        "disgust": 0.0,
        "anticipation": 0.4
      },
      "dominant_emotion": "joy",
      "confidence": 0.85
    }
  ]
}"""


def build_prompt(comments: list[dict]) -> str:
    lines = ["Aşağıdaki yorumları analiz et:\n"]
    for c in comments:
        text = c["text"][:400] if len(c["text"]) > 400 else c["text"]
        lines.append(f'comment_id: "{c["comment_id"]}" | yorum: "{text}"')
    return "\n".join(lines)


def _parse_llm_response(raw: str) -> list[dict]:
    """
    Markdown fence, BOM, trailing garbage ne olursa olsun JSON parse eder.
    Birden fazla strateji dener, hepsi başarısız olursa boş liste döner.
    """
    if not raw:
        return []

    # 1) BOM ve baştaki/sondaki boşlukları temizle
    text = raw.strip().lstrip("\ufeff")

    # 2) Markdown kod bloğu varsa içini al  (```json ... ``` veya ``` ... ```)
    if "```" in text:
        parts = text.split("```")
        # çift backtick bloğunun içi: index 1, 3, 5 ...
        for i in range(1, len(parts), 2):
            candidate = parts[i].strip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{") or candidate.startswith("["):
                text = candidate
                break

    # 3) İlk { veya [ ile başlayan kısmı bul (önünde açıklama metni olabilir)
    for start_char in ("{", "["):
        idx = text.find(start_char)
        if idx != -1:
            text = text[idx:]
            break

    # 4) Sondaki gereksiz karakterleri temizle (} veya ] sonrası)
    for end_char in ("}", "]"):
        last = text.rfind(end_char)
        if last != -1:
            text = text[: last + 1]
            break

    # 5) Parse dene
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # {"results": [...]} formatı
            for key in ("results", "data", "analyses", "output"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            # Tek obje geldiyse listeye sar
            if "comment_id" in data:
                return [data]
        return []
    except json.JSONDecodeError as e:
        logger.debug(f"JSON parse başarısız: {e}\nHam yanıt: {raw[:300]}")
        return []


# ── Analyzer sınıfları ────────────────────────────────────────────────────────

class GPTAnalyzer:
    """OpenAI GPT ile duygu analizi."""

    def __init__(self):
        if OpenAI is None:
            raise ImportError(
                "openai paketi yüklü değil.\n"
                "Çözüm: pip install openai"
            )
        if not settings.chatgpt_api_key:
            raise ValueError(
                "CHATGPT_API_KEY .env dosyasında bulunamadı.\n"
                "Kontrol et: .env içinde CHATGPT_API_KEY=sk-... satırı var mı?"
            )
        self.client = OpenAI(api_key=settings.chatgpt_api_key)
        self.model = settings.chatgpt_model  # default: gpt-4o-mini

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def analyze_batch(self, comments: list[dict]) -> list[dict]:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=settings.llm_max_tokens,
            temperature=0.2,                        # düşük temp → tutarlı JSON
            response_format={"type": "json_object"}, # JSON modunu zorla
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_prompt(comments)},
            ],
        )
        raw = response.choices[0].message.content.strip()
        return _parse_llm_response(raw)


class ClaudeAnalyzer:
    """Anthropic Claude ile duygu analizi."""

    def __init__(self):
        if anthropic is None:
            raise ImportError("anthropic paketi yüklü değil.\nÇözüm: pip install anthropic")
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY .env dosyasında bulunamadı.")
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def analyze_batch(self, comments: list[dict]) -> list[dict]:
        message = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=settings.llm_max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(comments)}],
        )
        raw = message.content[0].text.strip()
        return _parse_llm_response(raw)


class GeminiAnalyzer:
    """Google Gemini ile duygu analizi."""

    def __init__(self):
        if genai is None:
            raise ImportError("google-generativeai paketi yüklü değil.\nÇözüm: pip install google-generativeai")
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY .env dosyasında bulunamadı.")
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def analyze_batch(self, comments: list[dict]) -> list[dict]:
        response = self.model.generate_content(build_prompt(comments))
        raw = response.text.strip()
        return _parse_llm_response(raw)


def _get_analyzer():
    """LLM_PROVIDER değerine göre doğru analyzer'ı döndürür."""
    provider = (settings.llm_provider or "").lower().strip()

    if provider in ("chatgpt", "openai", "gpt"):
        console.print(f"  LLM: [bold green]OpenAI GPT[/bold green] → model: [dim]{settings.chatgpt_model}[/dim]")
        return GPTAnalyzer()
    elif provider == "gemini":
        console.print("  LLM: [bold yellow]Google Gemini[/bold yellow] → model: [dim]gemini-1.5-flash[/dim]")
        return GeminiAnalyzer()
    elif provider == "claude":
        console.print("  LLM: [bold blue]Anthropic Claude[/bold blue] → model: [dim]claude-opus-4-5[/dim]")
        return ClaudeAnalyzer()
    else:
        console.print(
            f"[red]Bilinmeyen LLM_PROVIDER: '{provider}'[/red]\n"
            "Geçerli değerler: chatgpt | gemini | claude\n"
            "[yellow]Varsayılan olarak GPT seçildi.[/yellow]"
        )
        return GPTAnalyzer()


# ── Aggregation ───────────────────────────────────────────────────────────────

def aggregate_sentiment(
    analyzed: list[AnalyzedComment],
) -> tuple[SentimentScore, str, dict]:
    if not analyzed:
        return (
            SentimentScore(
                anger=0, joy=0, trust=0, fear=0,
                surprise=0, sadness=0, disgust=0, anticipation=0,
            ),
            "neutral",
            {},
        )

    fields = ["anger", "joy", "trust", "fear", "surprise", "sadness", "disgust", "anticipation"]
    totals = {f: 0.0 for f in fields}
    distribution: dict[str, int] = {}

    for ac in analyzed:
        for f in fields:
            totals[f] += getattr(ac.sentiment, f)
        distribution[ac.dominant_emotion] = distribution.get(ac.dominant_emotion, 0) + 1

    n = len(analyzed)
    avg = {f: round(totals[f] / n, 4) for f in fields}
    dominant = max(avg, key=avg.__getitem__)

    return SentimentScore(**avg), dominant, distribution


# ── Ana çalıştırıcı ───────────────────────────────────────────────────────────

def run_brain(input_path: Path | None = None) -> Path:
    if input_path is None:
        raw_files = sorted(settings.raw_data_dir.glob("fetch_*.json"), reverse=True)
        if not raw_files:
            console.print(
                "[red]Hata:[/red] raw_data/ klasöründe dosya yok.\n"
                "Önce Ajan 1'i çalıştır: [bold]python agents/fetcher.py[/bold]"
            )
            raise SystemExit(1)
        input_path = raw_files[0]

    console.rule("[bold purple]Agent 2: The Brain[/bold purple]")
    console.print(f"  Girdi: [dim]{input_path.name}[/dim]")

    with open(input_path, encoding="utf-8") as f:
        raw = json.load(f)

    videos = raw.get("videos", [])
    analyzer = _get_analyzer()

    results = []
    total_calls = 0

    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console
    ) as progress:
        task = progress.add_task("Analiz ediliyor...", total=len(videos))

        for video_dict in videos:
            video = VideoData(**video_dict)
            comments = video.comments

            progress.update(task, description=f"[cyan]{video.title[:50]}[/cyan]")

            if not comments:
                progress.advance(task)
                continue

            batch_size = settings.sentiment_batch_size
            analyzed: list[AnalyzedComment] = []
            comment_dicts = [c.model_dump(mode="json") for c in comments]

            for i in range(0, len(comment_dicts), batch_size):
                batch = comment_dicts[i : i + batch_size]
                try:
                    llm_results = analyzer.analyze_batch(batch)
                    total_calls += 1

                    for res in llm_results:
                        try:
                            analyzed.append(
                                AnalyzedComment(
                                    comment_id=res["comment_id"],
                                    text=next(
                                        (c["text"] for c in batch if c["comment_id"] == res["comment_id"]),
                                        "",
                                    ),
                                    sentiment=SentimentScore(**res["scores"]),
                                    dominant_emotion=res["dominant_emotion"],
                                    confidence=res.get("confidence", 0.8),
                                )
                            )
                        except Exception as e:
                            logger.debug(f"Sonuç atlandı: {e}")

                except Exception as e:
                    logger.error(f"Batch hatası ({video.video_id}): {e}")

            agg_sentiment, dominant, distribution = aggregate_sentiment(analyzed)

            results.append(
                VideoAnalysis(
                    video_id=video.video_id,
                    title=video.title,
                    channel_name=video.channel_name,
                    category_id=video.category_id,
                    category_name=video.category_name,
                    view_count=video.view_count,
                    like_count=video.like_count,
                    thumbnail_url=video.thumbnail_url,
                    total_comments_analyzed=len(analyzed),
                    aggregate_sentiment=agg_sentiment,
                    dominant_emotion=dominant,
                    sentiment_distribution=distribution,
                    analyzed_comments=analyzed,
                ).model_dump(mode="json")
            )

            progress.advance(task)

    # ── Kaydet ──────────────────────────────────────────────────────────────
    settings.ensure_dirs()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = settings.processed_data_dir / f"analysis_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "analyzed_at": timestamp,
                    "llm_provider": settings.llm_provider,
                    "llm_model": settings.chatgpt_model if "gpt" in settings.llm_provider else settings.llm_provider,
                    "total_videos_analyzed": len(results),
                    "total_api_calls": total_calls,
                },
                "analyses": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    console.print(
        f"\n[green]✓ Tamamlandı![/green]  "
        f"{len(results)} video  |  {total_calls} API çağrısı  |  "
        f"Çıktı: [bold]{output_path}[/bold]"
    )
    return output_path


if __name__ == "__main__":
    run_brain()