from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def load_summary_module():
    path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "summarize_p57_packaged_launcher_economics.py"
    )
    spec = importlib.util.spec_from_file_location("summarize_p57_packaged_launcher", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_prefers_authoritative_model_provenance(tmp_path: Path) -> None:
    module = load_summary_module()
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "summary_id": "run_with_provenance",
                "status": "accepted-candidate",
                "accepted_candidate": True,
                "model": "self-reported-wrong-model",
                "model_provenance": {
                    "expected_model": "qwen3.6:35b-a3b-bf16",
                    "authoritative_model": "qwen3.6:35b-a3b-bf16",
                    "observed_model": "qwen3.6:35b-a3b-bf16",
                    "source": "copilot_chat_bridge_report",
                    "match_status": "matched",
                    "self_report_status": "not_applicable",
                },
                "source_count": 5,
                "subagent_tool_observed": True,
                "token_costs": {
                    "estimated_paid_cost_usd": 0.1,
                    "estimated_paid_cost_per_source_artifact_usd": 0.02,
                    "economics_usable": True,
                    "codex_total_token_delta": 1000,
                    "measurement_boundary": "external_coordinator_span",
                },
            }
        ),
        encoding="utf-8",
    )

    record = module.normalize(summary_path)

    assert record["model"] == "qwen3.6:35b-a3b-bf16"
    assert record["quality_validated_candidate"] is True
    assert record["protocol_accepted_candidate"] is True
    assert record["final_decision"] == "accepted_economics_evidence"
    assert record["subagent_tool_observed"] is True
    assert record["model_provenance"] == {
        "expected_model": "qwen3.6:35b-a3b-bf16",
        "authoritative_model": "qwen3.6:35b-a3b-bf16",
        "observed_model": "qwen3.6:35b-a3b-bf16",
        "source": "copilot_chat_bridge_report",
        "match_status": "matched",
        "self_report_status": "not_applicable",
    }


def test_normalize_marks_legacy_model_field(tmp_path: Path) -> None:
    module = load_summary_module()
    summary_path = tmp_path / "legacy_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "summary_id": "legacy_run",
                "status": "accepted-candidate",
                "model": "qwen3.6:35b-a3b-bf16",
                "source_count": 1,
                "token_costs": {
                    "estimated_paid_cost_usd": 0.1,
                    "economics_usable": True,
                    "codex_total_token_delta": 1000,
                },
            }
        ),
        encoding="utf-8",
    )

    record = module.normalize(summary_path)

    assert record["model"] == "qwen3.6:35b-a3b-bf16"
    assert record["quality_validated_candidate"] is True
    assert record["protocol_accepted_candidate"] is True
    assert record["final_decision"] == "accepted_economics_evidence"
    assert record["model_provenance"]["source"] == "legacy_model_field"
    assert record["model_provenance"]["match_status"] == "legacy_unavailable"
    assert record["model_provenance"]["self_report_status"] == "legacy_unavailable"
