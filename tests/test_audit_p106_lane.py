import json
from pathlib import Path

from scripts.audit_p106_lane import audit_lane


ROOT = Path(__file__).parents[1]
P89 = ROOT / "benchmarks/document_library/p89_jsonl_validation_contract.json"
P105 = ROOT / "benchmarks/document_library/p105_matched_benchmark_contract.json"


def record(kind: str, index: int, quote: str) -> dict[str, object]:
    return {
        "record_id": f"r-{index}",
        "corpus_id": "bc_tsr_tsa23_public_1995_present",
        "document_id": "tsa23_2012_23tsdp12",
        "source_sha256": "b334d15b71824c91460ad59bc0cc1ed5a7bed7efea4dd4d22eba0279e26cfedf",
        "chunk_id": "tsa23_2012_23tsdp12::pages_001_008",
        "page_anchor": "PDF page 1",
        "document_component": "component",
        "section_path": "section",
        "object_type": kind,
        "record_pass": "structure" if kind == "heading" else "content_metadata",
        "title": "Title",
        "summary": "Summary",
        "source_quote": quote,
        "confidence": 0.9,
        "worker_model": "worker",
        "review_status": "raw_worker_candidate",
    }


def test_p106_lane_audit_passes_exact_anchors(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("Exact structure quote. Exact content quote.", encoding="utf-8")
    output = tmp_path / "output.jsonl"
    rows = [record("heading", i, "Exact structure quote.") for i in range(3)]
    rows += [record("claim", i + 3, "Exact content quote.") for i in range(3)]
    rows += [record("definition", i + 6, "Exact content quote.") for i in range(3)]
    output.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    result = audit_lane(output=output, source_text=source, p89_contract=P89, p105_contract=P105, lane="direct", model="GPT-5.6 Luna")
    assert result["quality_gate"] == "pass"
    assert result["useful_yield"] == 1.0


def test_p106_lane_audit_rejects_anchor_defect(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("Exact quote.", encoding="utf-8")
    output = tmp_path / "output.jsonl"
    output.write_text(json.dumps(record("heading", 1, "Invented quote.")), encoding="utf-8")
    result = audit_lane(output=output, source_text=source, p89_contract=P89, p105_contract=P105, lane="delegated", model="worker")
    assert result["quality_gate"] == "fail"
    assert result["critical_source_anchor_defect_count"] == 1
