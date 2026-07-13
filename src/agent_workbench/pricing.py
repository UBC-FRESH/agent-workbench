"""Dated model-price catalog validation and resolution."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

DEFAULT_CATALOG = Path(__file__).resolve().parents[2] / "model_profiles" / "pricing_catalog.json"


@dataclass(frozen=True)
class PriceResolution:
    catalog_id: str
    catalog_version: int
    model_id: str
    effective_from: str
    verified_utc: str
    source_url: str
    input_per_1m_usd: float
    cached_input_read_per_1m_usd: float
    cache_write_per_1m_usd: float
    output_per_1m_usd: float
    long_context_threshold_tokens: int
    long_context_input_multiplier: float
    long_context_output_multiplier: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_price_catalog(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("price catalog must contain a JSON object")
    return data


def validate_price_catalog(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if not isinstance(data.get("catalog_id"), str) or not data.get("catalog_id"):
        errors.append("catalog_id must be a non-empty string")
    if not isinstance(data.get("catalog_version"), int) or data.get("catalog_version", 0) < 1:
        errors.append("catalog_version must be a positive integer")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["entries must be a non-empty array"]
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        prefix = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        model_id = entry.get("model_id")
        effective = entry.get("effective_from")
        if not isinstance(model_id, str) or not model_id:
            errors.append(f"{prefix}.model_id must be a non-empty string")
        try:
            date.fromisoformat(str(effective))
        except ValueError:
            errors.append(f"{prefix}.effective_from must be YYYY-MM-DD")
        key = (str(model_id), str(effective))
        if key in seen:
            errors.append(f"duplicate model/effective date: {key[0]} {key[1]}")
        seen.add(key)
        for field in ("verified_utc", "source_url"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                errors.append(f"{prefix}.{field} must be a non-empty string")
        rates = entry.get("rates")
        if not isinstance(rates, dict):
            errors.append(f"{prefix}.rates must be an object")
        else:
            for field in (
                "input_per_1m_usd",
                "cached_input_read_per_1m_usd",
                "cache_write_multiplier",
                "output_per_1m_usd",
            ):
                if not _positive_number(rates.get(field)):
                    errors.append(f"{prefix}.rates.{field} must be positive")
        long_context = entry.get("long_context")
        if not isinstance(long_context, dict):
            errors.append(f"{prefix}.long_context must be an object")
        else:
            if not isinstance(long_context.get("threshold_tokens"), int) or long_context.get("threshold_tokens", 0) < 1:
                errors.append(f"{prefix}.long_context.threshold_tokens must be positive")
            for field in ("input_multiplier", "output_multiplier"):
                if not _positive_number(long_context.get(field)):
                    errors.append(f"{prefix}.long_context.{field} must be positive")
    return errors


def resolve_model_price(
    data: dict[str, Any], model_id: str, as_of: str
) -> PriceResolution:
    errors = validate_price_catalog(data)
    if errors:
        raise ValueError("invalid price catalog: " + "; ".join(errors))
    target_date = date.fromisoformat(as_of)
    candidates = [
        entry
        for entry in data["entries"]
        if entry["model_id"] == model_id
        and date.fromisoformat(entry["effective_from"]) <= target_date
    ]
    if not candidates:
        raise ValueError(f"no price for model {model_id!r} on {as_of}")
    entry = max(candidates, key=lambda item: item["effective_from"])
    rates = entry["rates"]
    long_context = entry["long_context"]
    return PriceResolution(
        catalog_id=data["catalog_id"],
        catalog_version=data["catalog_version"],
        model_id=model_id,
        effective_from=entry["effective_from"],
        verified_utc=entry["verified_utc"],
        source_url=entry["source_url"],
        input_per_1m_usd=float(rates["input_per_1m_usd"]),
        cached_input_read_per_1m_usd=float(rates["cached_input_read_per_1m_usd"]),
        cache_write_per_1m_usd=float(rates["input_per_1m_usd"])
        * float(rates["cache_write_multiplier"]),
        output_per_1m_usd=float(rates["output_per_1m_usd"]),
        long_context_threshold_tokens=int(long_context["threshold_tokens"]),
        long_context_input_multiplier=float(long_context["input_multiplier"]),
        long_context_output_multiplier=float(long_context["output_multiplier"]),
    )


def _positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


# CLI-facing aliases retained as the compact public command surface.
def load_catalog(path: Path) -> dict[str, Any]:
    data = load_price_catalog(path)
    errors = validate_price_catalog(data)
    if errors:
        raise ValueError("invalid price catalog: " + "; ".join(errors))
    return data


def resolve_price(model_id: str, as_of: str | None, path: Path = DEFAULT_CATALOG) -> PriceResolution:
    return resolve_model_price(load_catalog(path), model_id, as_of or date.today().isoformat())
