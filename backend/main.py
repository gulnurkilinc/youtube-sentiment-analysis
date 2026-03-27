from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

sys.path.insert(0, str(Path(__file__).parent))
from agents.fetcher import run_fetcher
from agents.brain import run_brain
from config import settings

console = Console()


def main():
    start = datetime.utcnow()

    console.print(
        Panel.fit(
            "[bold]YouTube Duygu Analizi[/bold]\n"
            "[dim]3 Ajanlı Pipeline Sistemi[/dim]",
            border_style="blue",
        )
    )

    settings.ensure_dirs()

    # Agent 1
    console.print("\n[bold blue]⟶ Aşama 1/3: Veri Çekme (The Fetcher)[/bold blue]")
    raw_path = run_fetcher()

    # Agent 2
    console.print("\n[bold purple]⟶ Aşama 2/3: Duygu Analizi (The Brain)[/bold purple]")
    processed_path = run_brain(input_path=raw_path)

    # Agent 3 bilgi
    elapsed = (datetime.utcnow() - start).seconds
    console.print("\n[bold green]⟶ Aşama 3/3: Dashboard (The Visualizer)[/bold green]")
    console.print(
        f"  Veri hazır: [bold]{processed_path}[/bold]\n\n"
        f"  Frontend'i başlatmak için:\n"
        f"    [cyan]cd frontend[/cyan]\n"
        f"    [cyan]npm run dev[/cyan]\n"
    )

    console.print(
        Panel.fit(
            f"[green]✓ Pipeline tamamlandı![/green]\n"
            f"Süre: {elapsed} saniye",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()