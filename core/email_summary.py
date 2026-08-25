from typing import List

from core.schema import Evidence, StatusEnum


class EmailExposureSummary:
    @staticmethod
    def build(results: List[Evidence]) -> dict:
        found_sources = [
            result.source_name
            for result in results
            if result.status == StatusEnum.FOUND
        ]

        not_found_sources = [
            result.source_name
            for result in results
            if result.status == StatusEnum.NOT_FOUND
        ]

        unavailable_sources = [
            result.source_name
            for result in results
            if result.status in (
                StatusEnum.ERROR,
                StatusEnum.RATE_LIMITED,
                StatusEnum.BLOCKED,
            )
        ]

        uncertain_sources = [
            result.source_name
            for result in results
            if result.status == StatusEnum.UNKNOWN
        ]

        public_trace_count = len(found_sources)
        checked_source_count = len(results)


        return {
            "public_trace_count": public_trace_count,
            "checked_source_count": checked_source_count,
            "found_sources": found_sources,
            "not_found_sources": not_found_sources,
            "unavailable_sources": unavailable_sources,
            "uncertain_sources": uncertain_sources,
        }
