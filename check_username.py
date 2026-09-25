import asyncio
import sys
from datetime import datetime, timezone

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.platforms import PLATFORMS
from core.collector import HTTPCollector
from core.continuation import run_continuation_action
from core.normalizer import Normalizer
from core.reporting import save_json_report
from core.schema import EntityType, StatusEnum
from core.validators import UsernameValidator
from core.username_summary import build_username_summary
from core.youtube_discovery import discover_youtube_channels


console = Console()


STATUS_STYLES = {
    StatusEnum.FOUND: "bold green",
    StatusEnum.NOT_FOUND: "bright_black",
    StatusEnum.BLOCKED: "bold yellow",
    StatusEnum.RATE_LIMITED: "yellow",
    StatusEnum.UNKNOWN: "magenta",
    StatusEnum.ERROR: "bold red",
}


def format_datetime(value):
    if not value:
        return None

    try:
        normalized_value = value.replace(
            "Z",
            "+00:00",
        )

        parsed = datetime.fromisoformat(
            normalized_value
        )

        parsed_utc = parsed.astimezone(
            timezone.utc
        )

        return parsed_utc.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

    except (ValueError, TypeError):
        return str(value)


def add_detail_row(
    table: Table,
    label: str,
    value,
):
    """
    Додає рядок у CLI лише тоді,
    коли значення реально існує.
    """

    if value is not None and value != "":
        table.add_row(
            label,
            str(value),
        )


async def prompt_and_run_continuation(
    action,
    prompt_fn=None,
) -> bool:
    if action.get("status") != "ready":
        return False

    if prompt_fn is None:
        prompt_fn = input

    answer = prompt_fn(
        "Run this target? [y/N]: "
    ).strip().lower()

    if answer not in {
        "y",
        "yes",
    }:
        return False

    async def run_username(value):
        return await scan_username(
            value,
            allow_continuation=False,
        )

    return await run_continuation_action(
        action,
        {
            "username": run_username,
        },
    )


async def scan_username(
    raw_username: str,
    verbose: bool = False,
    allow_continuation: bool = True,
):
    normalized_username = Normalizer.normalize(
        EntityType.USERNAME,
        raw_username,
    )

    is_valid, reason = UsernameValidator.validate(
        normalized_username
    )

    if not is_valid:
        console.print(
            Panel(
                (
                    "[bold red]INVALID USERNAME[/bold red]"
                    f"\n{reason}"
                ),
                title="EXPOSURE ENGINE",
                border_style="red",
            )
        )

        return False

    console.print(
        Panel(
            (
                f"[bold]Target:[/bold]      "
                f"{raw_username}\n"
                f"[bold]Normalized:[/bold]  "
                f"{normalized_username}\n"
                f"[bold]Platforms:[/bold]   "
                f"{len(PLATFORMS)}"
            ),
            title="EXPOSURE ENGINE",
            border_style="cyan",
        )
    )

    youtube_candidates = []

    # Одна shared ClientSession
    # для всього scan.
    async with HTTPCollector() as collector:
        tasks = []

        for (
            source_name,
            platform_config,
        ) in PLATFORMS.items():

            task = collector.check_platform(
                entity_type=EntityType.USERNAME,
                raw_value=raw_username,
                normalized_value=normalized_username,
                source_name=source_name,
                platform_config=platform_config,
            )

            tasks.append(task)

        # Усі HTTP-запити завершуються,
        # поки shared session ще відкрита.
        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        source_names = list(PLATFORMS.keys())

        if "YouTube" in source_names:
            youtube_index = source_names.index("YouTube")
            youtube_result = results[youtube_index]

            if (
                not isinstance(youtube_result, Exception)
                and youtube_result.status == StatusEnum.NOT_FOUND
            ):
                youtube_candidates = await discover_youtube_channels(
                    collector,
                    normalized_username,
                )

    # Тут shared ClientSession вже закрита.
    evidence_results = []

    for source_name, result in zip(
        PLATFORMS.keys(),
        results,
    ):
        if isinstance(
            result,
            Exception,
        ):
            console.print(
                Panel(
                    (
                        "[bold red]ERROR[/bold red]"
                        f"\n{result}"
                    ),
                    title=source_name,
                    border_style="red",
                )
            )

            continue

        evidence_results.append(
            result
        )

        if not verbose:
            continue

        style = STATUS_STYLES.get(
            result.status,
            "white",
        )

        table = Table(
            show_header=False,
            box=None,
            padding=(0, 1),
        )

        table.add_column(
            "Field",
            style="bold",
            no_wrap=True,
        )

        table.add_column(
            "Value"
        )

        table.add_row(
            "Status",
            (
                f"[{style}]"
                f"{result.status.value.upper()}"
                f"[/{style}]"
            ),
        )

        table.add_row(
            "Confidence",
            result.confidence.value.upper(),
        )

        details = result.details

        add_detail_row(
            table,
            "HTTP",
            details.get(
                "http_status"
            ),
        )

        add_detail_row(
            table,
            "URL",
            details.get(
                "target_url"
            ),
        )

        if result.status == StatusEnum.FOUND:
            add_detail_row(
                table,
                "Username",
                details.get(
                    "username"
                ),
            )

            add_detail_row(
                table,
                "Name",
                details.get(
                    "name"
                ),
            )

            add_detail_row(
                table,
                "Display Name",
                details.get(
                    "display_name"
                ),
            )

            created_at = details.get(
                "created_at"
            )

            if created_at:
                add_detail_row(
                    table,
                    "Created At",
                    format_datetime(
                        created_at
                    ),
                )

            add_detail_row(
                table,
                "Public Repos",
                details.get(
                    "public_repos"
                ),
            )

            add_detail_row(
                table,
                "GitHub Username",
                details.get(
                    "github_username"
                ),
            )

            add_detail_row(
                table,
                "Location",
                details.get(
                    "location"
                ),
            )

            add_detail_row(
                table,
                "Website",
                details.get(
                    "website_url"
                ),
            )

            add_detail_row(
                table,
                "Karma",
                details.get(
                    "karma"
                ),
            )

            add_detail_row(
                table,
                "About",
                details.get(
                    "about"
                ),
            )

            add_detail_row(
                table,
                "Channel ID",
                details.get("channel_id"),
            )

            add_detail_row(
                table,
                "Title",
                details.get("title"),
            )

            add_detail_row(
                table,
                "Handle",
                details.get("custom_url"),
            )

            published_at = details.get("published_at")

            if published_at:
                add_detail_row(
                    table,
                    "Published At",
                    format_datetime(published_at),
                )

            add_detail_row(
                table,
                "Subscribers",
                details.get("subscriber_count"),
            )

            add_detail_row(
                table,
                "Videos",
                details.get("video_count"),
            )

            add_detail_row(
                table,
                "Views",
                details.get("view_count"),
            )

        add_detail_row(
            table,
            "Note",
            result.limitations,
        )

        console.print(
            Panel(
                table,
                title=source_name,
                border_style=style,
            )
        )

    if youtube_candidates:
        discovery_table = Table(
            box=box.SIMPLE,
            show_header=True,
        )

        discovery_table.add_column(
            "#",
            justify="right",
        )
        discovery_table.add_column("Title")
        discovery_table.add_column("Channel ID")

        for index, candidate in enumerate(
            youtube_candidates,
            start=1,
        ):
            discovery_table.add_row(
                str(index),
                candidate.get("title") or "-",
                candidate.get("channel_id") or "-",
            )

        console.print(
            Panel(
                discovery_table,
                title="POSSIBLE MATCHES",
                border_style="yellow",
                subtitle=(
                    "Discovery candidates only - "
                    "not confirmed identity matches."
                ),
            )
        )

    summary = build_username_summary(
        evidence_results
    )

    summary_table = Table(
        title="SCAN SUMMARY",
        box=box.ROUNDED,
    )

    summary_table.add_column(
        "Category"
    )

    summary_table.add_column(
        "Count",
        justify="right",
    )

    summary_table.add_row(
        "FOUND",
        str(len(summary["found_sources"])),
    )

    summary_table.add_row(
        "NOT_FOUND",
        str(len(summary["not_found_sources"])),
    )

    summary_table.add_row(
        "ATTENTION",
        str(len(summary["attention_sources"])),
    )

    console.print(
        summary_table
    )

    if summary["found_sources"]:
        console.print(
            "\n[bold green]FOUND SOURCES[/bold green]"
        )

        for source in summary["found_sources"]:
            console.print(
                f"  [green]✓[/green] {source}"
            )

    if summary["attention_sources"]:
        attention_table = Table(
            title="ATTENTION",
            box=box.SIMPLE,
        )

        attention_table.add_column(
            "Source"
        )

        attention_table.add_column(
            "Status"
        )

        for item in summary["attention_sources"]:
            attention_table.add_row(
                item["source"],
                item["status"].upper(),
            )

        console.print(
            attention_table
        )

    if summary["identity_signals"]:
        signals_table = Table(
            title="IDENTITY SIGNALS",
            box=box.SIMPLE,
        )

        signals_table.add_column(
            "Source"
        )

        signals_table.add_column(
            "Field"
        )

        signals_table.add_column(
            "Value"
        )

        for signal in summary["identity_signals"]:
            signals_table.add_row(
                signal["source"],
                signal["field"],
                str(signal["value"]),
            )

        console.print(
            signals_table
        )

        console.print(
            "[dim]Signals only - cross-platform identity "
            "is not confirmed.[/dim]"
        )

    if summary["pivots"]:
        pivots_table = Table(
            title="PIVOTS",
            box=box.SIMPLE,
        )

        pivots_table.add_column(
            "Type"
        )

        pivots_table.add_column(
            "Value"
        )

        pivots_table.add_column(
            "Sources"
        )

        for pivot in summary["pivots"]:
            pivots_table.add_row(
                pivot["type"],
                str(pivot["value"]),
                ", ".join(pivot["sources"]),
            )

        console.print(
            pivots_table
        )

        console.print(
            "[dim]Candidate pivots only - "
            "identity is not confirmed.[/dim]"
        )

    if summary["next_targets"]:
        targets_table = Table(
            title="NEXT TARGETS",
            box=box.SIMPLE,
        )

        targets_table.add_column(
            "Type"
        )

        targets_table.add_column(
            "Value"
        )

        targets_table.add_column(
            "Sources"
        )

        for target in summary["next_targets"]:
            targets_table.add_row(
                target["target_type"],
                str(target["value"]),
                ", ".join(target["sources"]),
            )

        console.print(
            targets_table
        )

        console.print(
            "[dim]Candidate next targets only - "
            "identity is not confirmed.[/dim]"
        )

    if summary["continuation_actions"]:
        continuation_table = Table(
            title="CONTINUATION",
            box=box.SIMPLE,
        )

        continuation_table.add_column(
            "Status"
        )
        continuation_table.add_column(
            "Scanner"
        )
        continuation_table.add_column(
            "Type"
        )
        continuation_table.add_column(
            "Value"
        )
        continuation_table.add_column(
            "Sources"
        )

        for action in summary["continuation_actions"]:
            continuation_table.add_row(
                action["status"],
                action["scanner"] or "n/a",
                action["target_type"],
                str(action["value"]),
                ", ".join(action["sources"]),
            )

        console.print(
            continuation_table
        )

    report_path = save_json_report(
        entity_type=EntityType.USERNAME,
        raw_value=raw_username,
        normalized_value=normalized_username,
        evidences=evidence_results,
    )

    console.print(
        f"\n[green]Report saved:[/green] "
        f"{report_path}"
    )

    if allow_continuation:
        ready_actions = [
            action
            for action in summary["continuation_actions"]
            if action["status"] == "ready"
        ]

        if ready_actions:
            await prompt_and_run_continuation(
                ready_actions[0]
            )

    return True


def main():
    try:
        raw_username = (
            sys.argv[1]
            if len(sys.argv) > 1
            else input(
                "Введи username для пошуку: "
            )
        )

        scan_completed = asyncio.run(
            scan_username(
                raw_username
            )
        )

        if not scan_completed:
            sys.exit(1)

    except KeyboardInterrupt:
        console.print(
            (
                "\n[yellow]"
                "Scan cancelled."
                "[/yellow]"
            )
        )

        sys.exit(0)


if __name__ == "__main__":
    main()
