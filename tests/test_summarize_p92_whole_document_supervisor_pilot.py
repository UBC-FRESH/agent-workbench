from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_p92_whole_document_supervisor_pilot.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("p92_summarizer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_packet_separates_quality_protocol_and_economics() -> None:
    module = load_script()
    packet = module.build_packet(
        sample_report(),
        sample_validation(),
        sample_bridge_report(),
        sample_token_record(),
    )

    assert packet["decision"] == "accept_seed_for_coordinator_audit"
    assert packet["quality_outcome"]["candidate_record_count"] == 1
    assert packet["protocol_outcome"]["bridge_deviation_count"] == 0
    assert packet["protocol_outcome"]["tool_names"] == ["agent", "create_file"]
    assert packet["economics_outcome"]["economics_decision"] == "not_yet_proven"
    assert packet["economics_outcome"]["cash_cost_usd"] == 0.087798


def test_cli_preserves_overridden_evidence_paths(tmp_path: Path) -> None:
    report = write_json(tmp_path / "report.json", sample_report())
    validation = write_json(tmp_path / "validation.json", sample_validation())
    token_record = write_json(tmp_path / "tokens.json", sample_token_record())
    bridge = tmp_path / "bridge.md"
    bridge.write_text(sample_bridge_report(), encoding="utf-8")
    output = tmp_path / "decision.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--report",
            str(report),
            "--validation",
            str(validation),
            "--bridge-report",
            str(bridge),
            "--token-record",
            str(token_record),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    packet = json.loads(output.read_text(encoding="utf-8"))
    assert packet["raw_evidence"]["report_path"] == report.as_posix()
    assert packet["raw_evidence"]["bridge_report_path"] == bridge.as_posix()


def write_json(path: Path, data: dict[str, object]) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def sample_report() -> dict[str, object]:
    return {
        "source_document_read": True,
        "final_signal": "job_complete_with_caveats",
        "next_action": "accept_seed",
        "output_quality": {"quality_validated_candidate": True},
        "gaps": ["one bounded audit remains"],
        "records": [
            {
                "record_id": "R01",
                "object_type": "document_metadata",
                "confidence": "high",
            }
        ],
    }


def sample_validation() -> dict[str, object]:
    return {"status": "valid", "fatal_error_count": 0, "candidate_record_count": 1}


def sample_bridge_report() -> str:
    return """status: accepted-candidate
resolved_model: qwen3.6:35b-a3b-bf16
model_match: true
permission_levels: autopilot
final_marker_present: true

## Tool Names

- `agent`
- `create_file`

## Deviations

- none
"""


def sample_token_record() -> dict[str, object]:
    return {
        "scope": {"phase": "P92"},
        "usage": {
            "supervisor_input_tokens": 1679,
            "supervisor_cached_input_tokens": 447232,
            "supervisor_output_tokens": 471,
            "supervisor_reasoning_output_tokens": 0,
            "codex_total_token_delta": 449382,
        },
        "prices": {
            "supervisor_input_price_per_1m_usd": 1.75,
            "supervisor_cached_input_price_per_1m_usd": 0.175,
            "supervisor_output_price_per_1m_usd": 14.0,
        },
    }
