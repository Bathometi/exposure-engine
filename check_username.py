import asyncio
import sys

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.schema import EntityType, StatusEnum
from core.normalizer import Normalizer
from core.collector import HTTPCollector
from core.reporting import save_json_report
from config.platforms import PLATFORMS


console = Console()


STATUS_STYLES = {
    StatusEnum.FOUND: "bold green",
    StatusEnum.NOT_FOUND: "bright_black",
    StatusEnum.BLOCKED: "bold yellow",
    StatusEnum.RATE_LIMITED: "yellow",
    StatusEnum.UNKNOWN: "magenta",
    StatusEnum.ERROR: "bold red",
}


async def scan_target(target_username: str):
    norm_user = Normalizer.normalize_username(target_username)

    header = (
        f"[bold]Target:[/bold]      {target_username}\n"
        f"[bold]Normalized:[/bold]  {norm_user}\n"
        f"[bold]Platforms:[/bold]   {len(PLATFORMS)}"
    )

    console.print()
    console.print(
        Panel(
            header,
            title="[bold cyan]EXPOSURE ENGINE[/bold cyan]",
            border_style="cyan",
        )
    )

    collector = HTTPCollector(timeout_seconds=5)

    tasks = []

    for platform_name, config in PLATFORMS.items():
        task = collector.check_platform(
            entity_type=EntityType.USERNAME,
            raw_value=target_username,
            normalized_value=norm_user,
            source_name=platform_name,
            platform_config=config,
        )

        tasks.append(task)

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    status_counts = {
        status: 0
        for status in StatusEnum
    }

    collector_errors = 0
    evidences = []

    for result in results:
        if isinstance(result, Exception):
            collector_errors += 1

            console.print(
                Panel(
                    f"[red]{result}[/red]",
                    title="[bold red]COLLECTOR ERROR[/bold red]",
                    border_style="red",
                )
            )

            continue

        evidence = result
        evidences.append(evidence)

        status_counts[evidence.status] += 1

        style = STATUS_STYLES.get(
            evidence.status,
            "white",
        )

        details_table = Table.grid(
            padding=(0, 2),
        )

        details_table.add_column(
            style="bold",
            width=13,
        )

        details_table.add_column()

        details_table.add_row(
            "Status",
            f"[{style}]{evidence.status.value.upper()}[/{style}]",
        )

        details_table.add_row(
            "Confidence",
            evidence.confidence.value.upper(),
        )

        http_status = evidence.details.get("http_status")

        if http_status is not None:
            details_table.add_row(
                "HTTP",
                str(http_status),
            )

        target_url = evidence.details.get("target_url")

        if target_url:
            details_table.add_row(
                "URL",
                target_url,
            )

        if evidence.status == StatusEnum.FOUND:
            detail_fields = {
                "username": "Username",
                "name": "Name",
                "created_at": "Created At",
                "public_repos": "Public Repos",
            }

            for key, label in detail_fields.items():
                value = evidence.details.get(key)

                if value is not None:
                    details_table.add_row(
                        label,
                        str(value),
                    )

        error_message = evidence.details.get("error")

        if error_message:
            details_table.add_row(
                "Error",
                f"[red]{error_message}[/red]",
            )

        if evidence.limitations:
            details_table.add_row(
                "Note",
                evidence.limitations,
            )

        console.print(
            Panel(
                details_table,
                title=(
                    f"[{style}]"
                    f"{evidence.source_name}"
                    f"[/{style}]"
                ),
                border_style=style,
            )
        )

    summary = Table(
        title="SCAN SUMMARY",
        box=box.ROUNDED,
        header_style="bold cyan",
    )

    summary.add_column(
        "Status",
        style="bold",
    )

    summary.add_column(
        "Count",
        justify="right",
    )

    for status in StatusEnum:
        style = STATUS_STYLES.get(
            status,
            "white",
        )

        summary.add_row(
            f"[{style}]{status.value.upper()}[/{style}]",
            str(status_counts[status]),
        )

    if collector_errors:
        summary.add_row(
            "[bold red]COLLECTOR ERROR[/bold red]",
            str(collector_errors),
        )

    console.print(summary)

    report_path = save_json_report(
        entity_type=EntityType.USERNAME,
        raw_value=target_username,
        normalized_value=norm_user,
        evidences=evidences,
    )

    console.print()
    console.print(
        f"[dim]Report saved:[/dim] "
        f"[cyan]{report_path}[/cyan]"
    )
    console.print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username_to_check = sys.argv[1]
    else:
        username_to_check = console.input(
            "[bold cyan]Введи username для пошуку:[/bold cyan] "
        )

    asyncio.run(
        scan_target(username_to_check)
    )
