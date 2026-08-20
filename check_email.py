import asyncio
import sys
from datetime import datetime, timezone

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.platforms import EMAIL_PLATFORMS
from core.collector import HTTPCollector
from core.normalizer import Normalizer
from core.reporting import save_json_report
from core.schema import EntityType, StatusEnum
from core.validators import EmailValidator


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


async def scan_email(
    raw_email: str,
):
    normalized_email = Normalizer.normalize(
        EntityType.EMAIL,
        raw_email,
    )

    is_valid, reason = EmailValidator.validate(
        normalized_email
    )

    if not is_valid:
        console.print(
            Panel(
                (
                    "[bold red]INVALID EMAIL[/bold red]"
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
                f"{raw_email}\n"
                f"[bold]Normalized:[/bold]  "
                f"{normalized_email}\n"
                f"[bold]Platforms:[/bold]   "
                f"{len(EMAIL_PLATFORMS)}"
            ),
            title="EXPOSURE ENGINE",
            border_style="cyan",
        )
    )

    # Одна shared ClientSession
    # для всього scan.
    async with HTTPCollector() as collector:
        tasks = []

        for (
            source_name,
            platform_config,
        ) in EMAIL_PLATFORMS.items():

            task = collector.check_platform(
                entity_type=EntityType.EMAIL,
                raw_value=raw_email,
                normalized_value=normalized_email,
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

    # Тут shared ClientSession вже закрита.
    evidence_results = []

    for source_name, result in zip(
        EMAIL_PLATFORMS.keys(),
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
                "Name",
                details.get(
                    "name"
                ),
            )
            add_detail_row(
                table,
                "Profile URL",
                details.get(
                    "profile_url"
                ),
            )

            add_detail_row(
                table,
                "Avatar URL",
                details.get(
                    "avatar_url"
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
                "About",
                details.get(
                    "about"
                ),
            )
            add_detail_row(
                table,
                "Job Title",
                details.get(
                    "job_title"
                ),
            )

            add_detail_row(
                table,
                "Company",
                details.get(
                    "company"
                ),
            )

            add_detail_row(
                table,
                "Hash",
                details.get(
                    "hash"
                ),
            )
            add_detail_row(
                table,
                "Breach Count",
                details.get(
                    "breach_count"
                ),
            )

            breaches = details.get(
                "breaches"
            )

            if breaches:
                add_detail_row(
                    table,
                    "Breaches",
                    ", ".join(breaches),
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

    summary_table = Table(
        title="SCAN SUMMARY",
        box=box.ROUNDED,
    )

    summary_table.add_column(
        "Status"
    )

    summary_table.add_column(
        "Count",
        justify="right",
    )

    for status in [
        StatusEnum.FOUND,
        StatusEnum.NOT_FOUND,
        StatusEnum.RATE_LIMITED,
        StatusEnum.BLOCKED,
        StatusEnum.UNKNOWN,
        StatusEnum.ERROR,
    ]:
        count = sum(
            1
            for result in evidence_results
            if result.status == status
        )

        summary_table.add_row(
            status.value.upper(),
            str(count),
        )

    console.print(
        summary_table
    )

    report_path = save_json_report(
        entity_type=EntityType.EMAIL,
        raw_value=raw_email,
        normalized_value=normalized_email,
        evidences=evidence_results,
    )

    console.print(
        f"\n[green]Report saved:[/green] "
        f"{report_path}"
    )

    return True


def main():
    try:
        raw_emails = sys.argv[1:]

        if not raw_emails:
            raw_emails = [
                input(
                    "Введи email для пошуку: "
                )
            ]

        all_completed = True

        for raw_email in raw_emails:
            scan_completed = asyncio.run(
                scan_email(
                    raw_email
                )
            )

            if not scan_completed:
                all_completed = False

        if not all_completed:
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
