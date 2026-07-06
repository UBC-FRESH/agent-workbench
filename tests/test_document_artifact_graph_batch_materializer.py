from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_graph_batch_materializer_splits_sources_and_generates_child_jobs(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "agent_jobs"
    sources = [
        "benchmarks/document_library/tsa23_tsr/p55_codex_vs_copilot_supervisor_ab_summary.json",
        "benchmarks/document_library/tsa23_tsr/p55_large_codex_vs_copilot_supervisor_ab_summary.json",
        "benchmarks/document_library/tsa23_tsr/p55_wave1_full_document_rerun_summary.json",
        "benchmarks/document_library/tsa23_tsr/p55_wave1_smoke_summary.json",
        "benchmarks/document_library/tsa23_tsr/p55_wave10_quote_repair_prepass_summary.json",
        "benchmarks/document_library/tsa23_tsr/p55_wave2_model_ab_summary.json",
    ]
    command = [
        sys.executable,
        str(ROOT / "scripts" / "materialize_document_artifact_graph_batch.py"),
        "--project-root",
        str(ROOT),
        "--output-dir",
        str(output_dir),
        "--job-id",
        "test_graph_batch",
        "--marker",
        "TEST_GRAPH_BATCH",
        "--batch-size",
        "5",
    ]
    for source in sources:
        command.extend(["--source-summary", source])

    completed = subprocess.run(command, cwd=tmp_path, text=True, check=False)

    assert completed.returncode == 0
    batch_manifest_path = output_dir / "test_graph_batch_batch_manifest.json"
    assert batch_manifest_path.exists()
    batch_manifest = json.loads(batch_manifest_path.read_text(encoding="utf-8"))
    assert batch_manifest["source_count"] == 6
    assert batch_manifest["batch_count"] == 2
    assert batch_manifest["batch_policy"]["max_source_summaries_per_graph_job"] == 5
    assert batch_manifest["jobs"][0]["source_summaries"] == sources[:5]
    assert batch_manifest["jobs"][1]["source_summaries"] == sources[5:]

    first_ticket = output_dir / "test_graph_batch_split_01_ticket.md"
    second_manifest = output_dir / "test_graph_batch_split_02_manifest.json"
    assert first_ticket.exists()
    assert second_manifest.exists()
    ticket = first_ticket.read_text(encoding="utf-8")
    assert "Materializer success is not completion" in ticket
    assert "verify_document_artifact_audit_report.py" in ticket
