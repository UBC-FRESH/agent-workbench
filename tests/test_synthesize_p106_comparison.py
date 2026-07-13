import json
from pathlib import Path

from scripts.synthesize_p106_comparison import build_packet


ROOT = Path(__file__).parents[1]
GATE = ROOT / "benchmarks/document_library/p106_matched_execution_gate.json"


def write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def token(path: Path, lane: str) -> Path:
    return write_json(path, {
        "record_id": f"{lane}-tokens",
        "source_type": "codex-session",
        "scope": {"phase": "P106", "span_id": lane},
        "generated_utc": "2026-07-13T00:00:00Z",
        "usage": {"supervisor_input_tokens": 1000, "supervisor_cached_input_tokens": 0, "supervisor_output_tokens": 100, "supervisor_reasoning_output_tokens": 0, "worker_input_tokens": 0, "worker_output_tokens": 0},
        "prices": {"supervisor_input_price_per_1m_usd": 1.0, "supervisor_cached_input_price_per_1m_usd": 0.1, "supervisor_output_price_per_1m_usd": 6.0, "worker_input_price_per_1m_usd": 0.0, "worker_output_price_per_1m_usd": 0.0},
        "pricing_provenance": {"qualified": True, "model_id": "gpt-5.6-luna", "effective_date": "2026-07-13", "price_source": "catalog"},
        "public_safety": {"raw_prompts_excluded": True, "raw_traces_excluded": True, "provider_urls_excluded": True, "headers_excluded": True, "personal_paths_excluded": True},
    })


def test_comparison_keeps_verdicts_separate(tmp_path: Path) -> None:
    summaries = []
    for lane in ("delegated", "direct"):
        summaries.append(write_json(tmp_path / f"{lane}.json", {"phase": "P106", "lane": lane, "model": "GPT-5.6 Luna", "record_count": 10, "useful_record_count": 10, "useful_yield": 1.0, "critical_source_anchor_defect_count": 0, "composition_ok": True, "quality_gate": "pass", "protocol_verdict": "pass"}))
    packet = build_packet(gate=GATE, delegated_summary=summaries[0], direct_summary=summaries[1], delegated_tokens=token(tmp_path / "d.tokens.json", "delegated"), direct_tokens=token(tmp_path / "x.tokens.json", "direct"))
    assert packet["status"] == "accepted-candidate"
    assert packet["verdicts"] == {"quality_validated_candidate": True, "protocol_accepted_candidate": True, "economics_usable": True}
