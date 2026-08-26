import json
import re

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from core.schema import Evidence, EntityType


def _safe_filename(value: str) -> str:
    cleaned = re.sub(
        r"[^a-zA-Z0-9_.-]+",
        "_",
        value,
    )

    return cleaned.strip("._") or "unknown"


def save_json_report(
    entity_type: EntityType,
    raw_value: str,
    normalized_value: str,
    evidences: Iterable[Evidence],
    enrichments: dict | None = None,
    analysis: dict | None = None,
    reports_dir: str = "reports",
) -> Path:
    reports_path = Path(reports_dir)

    reports_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d_%H-%M-%S")

    safe_target = _safe_filename(
        normalized_value
    )

    filename = (
        f"{timestamp}_"
        f"{entity_type.value}_"
        f"{safe_target}.json"
    )

    output_path = reports_path / filename

    evidence_list = list(evidences)

    report = {
        "scan": {
            "entity_type": entity_type.value,
            "raw_value": raw_value,
            "normalized_value": normalized_value,
            "scanned_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "results_count": len(evidence_list),
        },
        "results": [
            evidence.model_dump(
                mode="json"
            )
            for evidence in evidence_list
        ],
    }

    if enrichments is not None:
        report["enrichments"] = enrichments

    if analysis is not None:
        report["analysis"] = analysis

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output_path
