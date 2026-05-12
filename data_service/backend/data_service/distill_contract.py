"""Shared distill preview contract helpers for HTTP and CLI entrypoints."""

from __future__ import annotations

from typing import Any

from .service import DataService


DISTILL_LIMIT_MIN = 1
DISTILL_LIMIT_MAX = 200
DISTILL_LIMIT_DEFAULT = 20


def normalize_distill_limit(value: object, *, default: int = DISTILL_LIMIT_DEFAULT) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    return max(DISTILL_LIMIT_MIN, min(parsed, DISTILL_LIMIT_MAX))


def normalize_non_negative_float(value: object, *, field: str, default: float = 0.0) -> float:
    try:
        parsed = float(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number") from exc
    return max(0.0, parsed)


def normalize_optional_text(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def run_distill_contract(
    service: DataService,
    *,
    source_id: object = None,
    limit: object = DISTILL_LIMIT_DEFAULT,
    kind: object = None,
    typed_unit_type: object = None,
    min_importance: object = 0.0,
    llm_enriched_only: object = False,
    authority: object = None,
    min_source_weight: object = 0.0,
    min_source_density: object = 0.0,
) -> dict[str, Any]:
    return service.read_distill_bundle(
        source_id=normalize_optional_text(source_id),
        limit=normalize_distill_limit(limit),
        kind=normalize_optional_text(kind),
        typed_unit_type=normalize_optional_text(typed_unit_type),
        min_importance=normalize_non_negative_float(min_importance, field="min_importance"),
        llm_enriched_only=bool(llm_enriched_only),
        authority=normalize_optional_text(authority),
        min_source_weight=normalize_non_negative_float(min_source_weight, field="min_source_weight"),
        min_source_density=normalize_non_negative_float(min_source_density, field="min_source_density"),
    )
