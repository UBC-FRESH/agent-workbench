from __future__ import annotations

import importlib.util
from pathlib import Path


def load_summary_module():
    path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "summarize_p55_supervisor_ab.py"
    )
    spec = importlib.util.spec_from_file_location("summarize_p55_supervisor_ab", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bridge_model_mismatch_adds_soft_provenance_penalty() -> None:
    module = load_summary_module()
    lane = {
        "lane_id": "copilot_free_supervisor",
        "repair_model": "qwen3-coder-next:latest",
        "model_provenance": module.default_model_provenance("qwen3-coder-next:latest"),
        "rubric_score": {
            "max_score": 100.0,
            "total_penalty": 16.0,
            "hard_penalty": 0.0,
            "soft_penalty": 16.0,
            "score": 84.0,
        },
        "quality": {},
    }
    bridge = {"resolved_model": "qwen3.6:35b-a3b-bf16"}

    module.attach_model_provenance(lane, bridge)

    assert lane["model_provenance"] == {
        "reported_model": "qwen3-coder-next:latest",
        "observed_model": "qwen3.6:35b-a3b-bf16",
        "authoritative_model": "qwen3.6:35b-a3b-bf16",
        "status": "mismatch",
        "mismatch_penalty": 25.0,
    }
    assert lane["quality"]["model_provenance_mismatch"] is True
    assert lane["rubric_score"]["hard_penalty"] == 0.0
    assert lane["rubric_score"]["soft_penalty"] == 41.0
    assert lane["rubric_score"]["total_penalty"] == 41.0
    assert lane["rubric_score"]["score"] == 59.0


def test_matching_ollama_latest_suffix_does_not_penalize() -> None:
    module = load_summary_module()
    lane = {
        "lane_id": "copilot_free_supervisor",
        "repair_model": "qwen3.6:35b-a3b-bf16:latest",
        "model_provenance": module.default_model_provenance(
            "qwen3.6:35b-a3b-bf16:latest"
        ),
        "rubric_score": {
            "max_score": 100.0,
            "total_penalty": 0.0,
            "hard_penalty": 0.0,
            "soft_penalty": 0.0,
            "score": 100.0,
        },
        "quality": {},
    }
    bridge = {"resolved_model": "ollama-models/Ollama/qwen3.6:35b-a3b-bf16"}

    module.attach_model_provenance(lane, bridge)

    assert lane["model_provenance"]["status"] == "matched_or_unavailable"
    assert lane["model_provenance"]["mismatch_penalty"] == 0.0
    assert "model_provenance_mismatch" not in lane["quality"]
    assert lane["rubric_score"]["score"] == 100.0
