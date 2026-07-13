from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_workbench.pricing import (
    load_price_catalog,
    resolve_model_price,
    validate_price_catalog,
)


CATALOG = Path(__file__).parents[1] / "model_profiles" / "pricing_catalog.json"


def test_catalog_validates_and_resolves_luna() -> None:
    data = load_price_catalog(CATALOG)
    assert validate_price_catalog(data) == []
    price = resolve_model_price(data, "gpt-5.6-luna", "2026-07-13")
    assert price.input_per_1m_usd == 1.0
    assert price.cached_input_read_per_1m_usd == 0.1
    assert price.cache_write_per_1m_usd == 1.25
    assert price.output_per_1m_usd == 6.0
    assert price.long_context_threshold_tokens == 272000


def test_resolution_selects_latest_effective_entry() -> None:
    data = load_price_catalog(CATALOG)
    older = json.loads(json.dumps(data["entries"][-1]))
    older["effective_from"] = "2026-01-01"
    older["rates"]["input_per_1m_usd"] = 0.5
    data["entries"].append(older)
    assert resolve_model_price(data, "gpt-5.6-luna", "2026-06-01").input_per_1m_usd == 0.5
    assert resolve_model_price(data, "gpt-5.6-luna", "2026-07-13").input_per_1m_usd == 1.0


def test_unknown_model_fails_closed() -> None:
    data = load_price_catalog(CATALOG)
    with pytest.raises(ValueError, match="no price for model"):
        resolve_model_price(data, "unknown", "2026-07-13")


def test_invalid_catalog_reports_duplicate() -> None:
    data = load_price_catalog(CATALOG)
    data["entries"].append(json.loads(json.dumps(data["entries"][0])))
    assert any("duplicate model/effective date" in error for error in validate_price_catalog(data))
