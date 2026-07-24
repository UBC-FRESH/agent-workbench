from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = ROOT / "scripts" / "copilot_chat_bridge.py"


def load_bridge_module():
    spec = importlib.util.spec_from_file_location("copilot_chat_bridge", BRIDGE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_graph_ticket_command_extraction_includes_named_command_blocks() -> None:
    bridge = load_bridge_module()
    ticket = """
## Exact Materializer Command

```powershell
python C:\\repo\\scripts\\materialize_document_artifact_audit.py --project-root C:\\repo
```

## Graph Execution Requirements

```powershell
$env:PYTHONPATH = "C:\\repo\\src"; python -m agent_workbench.cli authority validate --kind report --input "runtime/agent_jobs/report.json"
```

## Required Graph Report

```json
{
  "report_id": "example",
  "graph_id": "document_artifact_audit_supervisor_graph"
}
```

```powershell
python C:\\repo\\scripts\\verify_document_artifact_graph_report.py --graph-report runtime/agent_jobs/graph_report.json --audit-report runtime/agent_jobs/report.json
```
"""

    commands = bridge.extract_expected_commands(ticket)

    assert commands == [
        "python C:\\repo\\scripts\\materialize_document_artifact_audit.py --project-root C:\\repo",
        '$env:PYTHONPATH = "C:\\repo\\src"; python -m agent_workbench.cli authority validate --kind report --input "runtime/agent_jobs/report.json"',
        "python C:\\repo\\scripts\\verify_document_artifact_graph_report.py --graph-report runtime/agent_jobs/graph_report.json --audit-report runtime/agent_jobs/report.json",
    ]


def test_graph_command_comparison_accepts_equivalent_repair_loop_commands() -> None:
    bridge = load_bridge_module()
    workspace_root = Path("C:/repo")
    expected = [
        bridge.normalize_command_for_comparison(
            "python C:\\repo\\scripts\\materialize_document_artifact_audit.py "
            "--project-root C:\\repo --output-dir C:\\repo\\runtime\\agent_jobs",
            workspace_root,
        ),
        bridge.normalize_command_for_comparison(
            '$env:PYTHONPATH = "C:\\repo\\src"; python -m agent_workbench.cli '
            'authority validate --kind report --input "runtime/agent_jobs/report.json"',
            workspace_root,
        ),
    ]
    observed = [
        bridge.normalize_command_for_comparison(
            '$env:PYTHONPATH = "C:\\repo\\src"; '
            "python scripts\\materialize_document_artifact_audit.py "
            "--project-root C:\\repo --output-dir C:\\repo\\runtime\\agent_jobs",
            workspace_root,
        ),
        bridge.normalize_command_for_comparison(
            '$env:PYTHONPATH = \\"C:\\repo\\src\\"; python -m agent_workbench.cli '
            'authority validate --kind report --input \\"runtime/agent_jobs/report.json\\"',
            workspace_root,
        ),
        bridge.normalize_command_for_comparison(
            '$env:PYTHONPATH = \\"C:\\repo\\src\\"; python -m agent_workbench.cli '
            'authority validate --kind report --input \\"runtime/agent_jobs/report.json\\"',
            workspace_root,
        ),
        bridge.normalize_command_for_comparison(
            'Test-Path "C:\\repo\\runtime\\agent_jobs\\report.json"',
            workspace_root,
        ),
        bridge.normalize_command_for_comparison(
            '(Test-Path "C:\\repo\\runtime\\agent_jobs\\report.json")',
            workspace_root,
        ),
    ]

    missing, extra, benign = bridge.compare_commands(expected, observed)

    assert missing == []
    assert extra == []
    assert benign == [
        "Test-Path runtime\\agent_jobs\\report.json",
        "(Test-Path runtime\\agent_jobs\\report.json)",
    ]


def test_graph_command_comparison_flags_repeated_materializer() -> None:
    bridge = load_bridge_module()
    workspace_root = Path("C:/repo")
    expected = [
        bridge.normalize_command_for_comparison(
            "python C:\\repo\\scripts\\materialize_document_artifact_audit.py "
            "--project-root C:\\repo --output-dir C:\\repo\\runtime\\agent_jobs",
            workspace_root,
        ),
        bridge.normalize_command_for_comparison(
            "python C:\\repo\\scripts\\verify_document_artifact_graph_report.py "
            "--graph-report runtime/agent_jobs/graph_report.json "
            "--audit-report runtime/agent_jobs/report.json",
            workspace_root,
        ),
    ]
    observed = [
        expected[0],
        expected[0],
        expected[1],
        expected[1],
    ]

    missing, extra, benign = bridge.compare_commands(expected, observed)

    assert missing == []
    assert extra == [expected[0]]
    assert benign == []


def test_command_comparison_accepts_quotes_around_simple_path_arguments() -> None:
    bridge = load_bridge_module()
    workspace_root = Path("C:/repo")
    expected = [
        bridge.normalize_command_for_comparison(
            "python C:\\repo\\scripts\\verify_document_artifact_graph_report.py "
            "--graph-report runtime/agent_jobs/graph_report.json "
            "--audit-report runtime/agent_jobs/report.json",
            workspace_root,
        ),
    ]
    observed = [
        bridge.normalize_command_for_comparison(
            "python scripts\\verify_document_artifact_graph_report.py "
            '--graph-report "runtime\\agent_jobs\\graph_report.json" '
            '--audit-report "runtime\\agent_jobs\\report.json"',
            workspace_root,
        ),
    ]

    missing, extra, benign = bridge.compare_commands(expected, observed)

    assert missing == []
    assert extra == []
    assert benign == []


def test_allowed_report_write_commands_are_benign() -> None:
    bridge = load_bridge_module()
    extra_commands = [
        '$reportId = "runtime\\agent_jobs\\report.json"; '
        "$json | ConvertFrom-Json | ConvertTo-Json -Depth 10 | "
        'Set-Content -Path $reportId -Encoding UTF8; Write-Host "model output saved"',
        '$graphReport | Set-Content -Path "runtime\\agent_jobs\\graph_report.json" '
        "-Encoding UTF8",
        "python -c \"import json; path = r'runtime\\agent_jobs\\report.json'; "
        "data=json.load(open(path)); data['verification']['score']=1.0; "
        "json.dump(data, open(path, 'w'), indent=2)\"",
        "[System.IO.File]::WriteAllText(runtime\\agent_jobs\\graph_report.json, "
        "$graph, ([System.Text.Encoding]::UTF8))",
        'Remove-Item "runtime\\agent_jobs\\report.json"',
    ]
    allowed_files = [
        "runtime/agent_jobs/report.json",
        "runtime/agent_jobs/graph_report.json",
    ]

    remaining, benign = bridge.classify_allowed_report_write_commands(
        extra_commands,
        allowed_files,
    )

    assert remaining == ['Remove-Item "runtime\\agent_jobs\\report.json"']
    assert benign == extra_commands[:4]


def test_allowed_document_library_report_write_commands_are_benign() -> None:
    bridge = load_bridge_module()
    report_path = (
        "runtime\\document_library\\tsa23_tsr\\p92_whole_document_supervisor_pilot"
        "\\reports\\p92_tsa23_2012_23tsdp12_supervisor_report.json"
    )
    extra_commands = [
        f'$json | Set-Content -Path "{report_path}" -Encoding UTF8',
        f"[System.IO.File]::WriteAllText('{report_path}', $json)",
        f'Remove-Item "{report_path}"',
    ]
    allowed_files = [
        report_path.replace("\\", "/"),
    ]

    remaining, benign = bridge.classify_allowed_report_write_commands(
        extra_commands,
        allowed_files,
    )

    assert remaining == [f'Remove-Item "{report_path}"']
    assert benign == extra_commands[:2]


def test_p92_ticket_report_path_is_extracted_as_allowed_file() -> None:
    bridge = load_bridge_module()
    ticket = """
## Workspace

- Report path to write: `runtime/document_library/tsa23_tsr/p92/reports/report.json`

## Required Output File

- `runtime/document_library/tsa23_tsr/p92/reports/report.json`
"""

    allowed_files = bridge.extract_allowed_files(ticket)

    assert allowed_files == [
        "runtime/document_library/tsa23_tsr/p92/reports/report.json"
    ]


def test_missing_conditional_repair_helper_is_not_a_deviation() -> None:
    bridge = load_bridge_module()
    expected = [
        "python scripts\\repair_document_artifact_graph_reports.py --audit-report runtime\\agent_jobs\\report.json",
        "python scripts\\verify_document_artifact_graph_report.py --graph-report runtime\\agent_jobs\\graph_report.json --audit-report runtime\\agent_jobs\\report.json",
    ]
    observed = [
        "python scripts\\verify_document_artifact_graph_report.py --graph-report runtime\\agent_jobs\\graph_report.json --audit-report runtime\\agent_jobs\\report.json",
    ]

    missing, extra, benign = bridge.compare_commands(expected, observed)

    assert missing == []
    assert extra == []
    assert benign == []


def test_if_test_path_runtime_check_is_benign() -> None:
    bridge = load_bridge_module()

    assert bridge.is_benign_extra_command(
        'if (Test-Path "runtime\\agent_jobs\\report.json") { Write-Host "exists" }'
    )


def test_final_marker_response_overrides_stale_model_state(tmp_path: Path) -> None:
    bridge = load_bridge_module()
    session = tmp_path / "session.jsonl"
    marker = "ORNITH35_S02_DONE"
    session.write_text(
        '{"message":{"text":"ticket marker: ORNITH35_S02_DONE"},'
        '"modelState":{"value":0},'
        '"metadata":{"toolCallRounds":['
        '{"response":"\\n\\nORNITH35_S02_DONE","toolCalls":[]}'
        ']}}',
        encoding="utf-8",
    )

    evidence = bridge.load_evidence(marker, session, None)

    assert evidence.final_marker_present is True
    assert evidence.completed is True


def test_ticket_marker_without_assistant_response_is_not_terminal(tmp_path: Path) -> None:
    bridge = load_bridge_module()
    session = tmp_path / "session.jsonl"
    marker = "ORNITH35_S02_DONE"
    session.write_text(
        '{"message":{"text":"ticket marker: ORNITH35_S02_DONE"},'
        '"modelState":{"value":0}}',
        encoding="utf-8",
    )

    evidence = bridge.load_evidence(marker, session, None)

    assert evidence.final_marker_present is False
    assert evidence.completed is False


def test_ui_text_final_marker_overrides_stale_model_state(tmp_path: Path) -> None:
    bridge = load_bridge_module()
    session = tmp_path / "session.jsonl"
    marker = "ORNITH35_S02_DONE"
    session.write_text(
        '{"message":{"text":"ticket marker: ORNITH35_S02_DONE"},'
        '"modelState":{"value":0},'
        '"response":[{"kind":"thinking","value":"done"},'
        '{"value":"\\n\\nORNITH35_S02_DONE",'
        '"supportThemeIcons":false}]}',
        encoding="utf-8",
    )

    evidence = bridge.load_evidence(marker, session, None)

    assert evidence.final_marker_present is True
    assert evidence.completed is True


def test_transcript_final_marker_with_no_chat_session(tmp_path: Path) -> None:
    """A final marker in a transcript with no chat-session record must be terminal."""
    bridge = load_bridge_module()
    transcript = tmp_path / "transcript.jsonl"
    marker = "ORNITH35_S11_DONE"
    transcript.write_text(
        '{"message":{"text":"ticket marker: ORNITH35_S11_DONE"},'
        '"modelState":{"value":0},'
        '"response":[{"value":"\\n\\nORNITH35_S11_DONE",'
        '"supportThemeIcons":false}]}',
        encoding="utf-8",
    )

    evidence = bridge.load_evidence(marker, None, transcript)

    assert evidence.final_marker_present is True
    assert evidence.completed is True
    assert evidence.transcript_path == transcript
    assert evidence.session_path is None


def test_ticket_attachment_marker_only_is_not_terminal(tmp_path: Path) -> None:
    """A marker appearing only in a ticket attachment must not count as terminal."""
    bridge = load_bridge_module()
    session = tmp_path / "session.jsonl"
    marker = "ORNITH35_S11_DONE"
    session.write_text(
        '{"message":{"text":"ticket marker: ORNITH35_S11_DONE"},'
        '"modelState":{"value":0}}',
        encoding="utf-8",
    )

    evidence = bridge.load_evidence(marker, session, None)

    assert evidence.final_marker_present is False
    assert evidence.completed is False


def test_transcript_stale_model_state_with_final_marker(tmp_path: Path) -> None:
    """A transcript with stale modelState but a final marker must still be terminal."""
    bridge = load_bridge_module()
    transcript = tmp_path / "transcript.jsonl"
    marker = "ORNITH35_S11_DONE"
    transcript.write_text(
        '{"message":{"text":"ticket marker: ORNITH35_S11_DONE"},'
        '"modelState":{"value":0},'
        '"response":[{"value":"\\n\\nORNITH35_S11_DONE",'
        '"supportThemeIcons":false}]}',
        encoding="utf-8",
    )

    evidence = bridge.load_evidence(marker, None, transcript)

    assert evidence.final_marker_present is True
    assert evidence.completed is True


def test_bridge_report_accepts_expected_model_match(tmp_path: Path) -> None:
    bridge = load_bridge_module()
    ticket = tmp_path / "ticket.md"
    ticket.write_text("Marker: MODEL_OK\n", encoding="utf-8")
    report = tmp_path / "report.md"
    evidence = bridge.SessionEvidence(
        session_path=tmp_path / "session.jsonl",
        resolved_model="qwen3.6:35b-a3b-bf16",
        final_marker_present=True,
        completed=True,
    )

    text = bridge.build_report(
        marker="MODEL_OK",
        ticket_path=ticket,
        report_path=report,
        workspace_root=tmp_path,
        ticket_text=ticket.read_text(encoding="utf-8"),
        evidence=evidence,
        expected_model="ollama-models/Ollama/qwen3.6:35b-a3b-bf16",
    )

    assert "status: accepted-candidate" in text
    assert "expected_model: ollama-models/Ollama/qwen3.6:35b-a3b-bf16" in text
    assert "resolved_model: qwen3.6:35b-a3b-bf16" in text
    assert "model_match: true" in text


def test_bridge_report_rejects_expected_model_mismatch(tmp_path: Path) -> None:
    bridge = load_bridge_module()
    ticket = tmp_path / "ticket.md"
    ticket.write_text("Marker: MODEL_BAD\n", encoding="utf-8")
    report = tmp_path / "report.md"
    evidence = bridge.SessionEvidence(
        session_path=tmp_path / "session.jsonl",
        resolved_model="qwen3-coder-next:latest",
        final_marker_present=True,
        completed=True,
    )

    text = bridge.build_report(
        marker="MODEL_BAD",
        ticket_path=ticket,
        report_path=report,
        workspace_root=tmp_path,
        ticket_text=ticket.read_text(encoding="utf-8"),
        evidence=evidence,
        expected_model="qwen3.6:35b-a3b-bf16",
    )

    assert "status: needs-supervisor-review" in text
    assert "model_match: false" in text
    assert "Resolved model did not match expected model." in text
