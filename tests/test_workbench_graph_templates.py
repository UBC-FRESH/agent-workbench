from __future__ import annotations

from pathlib import Path

from agent_workbench.graph import (
    decision_input_from_node,
    load_graph_document,
    validate_graph_document,
)


ROOT = Path(__file__).resolve().parents[1]


def test_document_artifact_audit_supervisor_graph_is_valid() -> None:
    path = (
        ROOT
        / "templates"
        / "workbench_templates"
        / "document_artifact_audit_supervisor_graph.json"
    )
    data = load_graph_document(path)

    result = validate_graph_document(data, source_path=path, agent_metadata=True)

    assert result.ok, [diagnostic.message for diagnostic in result.diagnostics]
    assert result.workflow_id == "document_artifact_audit_supervisor_graph"
    assert result.node_count == 6


def test_graph_decision_inputs_include_expected_verification() -> None:
    path = (
        ROOT
        / "templates"
        / "workbench_templates"
        / "document_artifact_audit_supervisor_graph.json"
    )
    data = load_graph_document(path)

    for node in data["nodes"]:
        decision_input = decision_input_from_node(node)
        assert decision_input["expected_verification"]


def test_graph_decision_inputs_map_role_authority_levels() -> None:
    path = (
        ROOT
        / "templates"
        / "workbench_templates"
        / "document_artifact_audit_supervisor_graph.json"
    )
    data = load_graph_document(path)
    by_id = {
        node["id"]: decision_input_from_node(node)["authority_level"]
        for node in data["nodes"]
    }

    assert by_id["subagent_artifact_audit"] == "L1"
    assert by_id["materialize_runtime_job"] == "L6"
    assert by_id["coordinator_job_ticket"] == "L6"
