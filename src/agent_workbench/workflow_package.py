"""Validated multi-step workflow package loading and rendering."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from .evidence import find_private_values


SCHEMA_VERSION = "workflow_package_v1"


@dataclass
class StepResult:
    step_id: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    input_artifacts: list[str] = field(default_factory=list)
    output_artifacts: list[str] = field(default_factory=list)
    _order_id: int = 9999


@dataclass
class PackageResult:
    ok: bool
    step_order: list[str] = field(default_factory=list)
    steps: list[StepResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def load_workflow_package(manifest_path):
    if not manifest_path.is_file():
        raise ValueError(f"manifest not found: {manifest_path}")

    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("workflow package manifest must be a JSON object")

    schema_version = data.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {schema_version!r} "
            f"(expected {SCHEMA_VERSION!r})"
        )

    steps_list = data.get("steps")
    if not isinstance(steps_list, list) or not steps_list:
        raise ValueError("'steps' must be a non-empty list of step file paths")

    package_root = manifest_path.resolve().parent
    loaded = {}

    for entry in steps_list:
        if not isinstance(entry, str):
            raise ValueError(f"step entry must be a string path, got {entry!r}")

        resolved = (package_root / entry).resolve()
        # Normalize to forward-slash paths for comparison across OS boundaries.
        norm_resolved = str(resolved).replace("\\", "/")
        norm_root = str(package_root).replace("\\", "/") + "/"
        if not norm_resolved.startswith(norm_root):
            raise ValueError(f"path escapes package root: {entry}")

        if not resolved.is_file():
            raise ValueError(f"step file not found: {entry}")

        step_data = json.loads(resolved.read_text(encoding="utf-8-sig"))
        if not isinstance(step_data, dict):
            raise ValueError(f"step record in {entry} must be a JSON object")

        loaded[entry] = step_data

    return {"manifest": data, "steps": loaded}


def validate_workflow_package(package, manifest_path=None):
    from .workflow import validate_workflow_step

    manifest = package["manifest"]
    steps_data = package["steps"]
    all_errors = []
    step_results = []
    produced_artifacts = {}
    seen_producer = set()

    for entry_path in manifest["steps"]:
        record = steps_data[entry_path]
        step_id = record.get("step_id", entry_path)
        valid_result = validate_workflow_step(record)
        inputs = [a.get("artifact_id", "") for a in record.get("input_artifacts", [])]
        outputs = [a.get("artifact_id", "") for a in record.get("output_artifacts", [])]

        for finding in find_private_values(record):
            valid_result = replace(
                valid_result, errors=valid_result.errors + ["private-looking value detected: " + finding]
            )

        step_results.append(StepResult(
            step_id=step_id,
            valid=valid_result.ok,
            errors=list(valid_result.errors),
            input_artifacts=inputs,
            output_artifacts=outputs,
        ))

    seen_step_ids = set()
    duplicate_step_ids = set()
    for sr in step_results:
        if sr.step_id in seen_step_ids:
            duplicate_step_ids.add(sr.step_id)
            all_errors.append("duplicate step_id: " + sr.step_id)
        seen_step_ids.add(sr.step_id)

    for sr in step_results:
        seen_in_step = set()
        for oid in sr.output_artifacts:
            if oid in produced_artifacts or oid in seen_in_step:
                if oid not in seen_in_step:
                    all_errors.append("duplicate produced artifact_id: " + oid)
                else:
                    all_errors.append("duplicate produced artifact_id: " + oid)
            elif oid not in produced_artifacts:
                produced_artifacts[oid] = sr.step_id
            seen_in_step.add(oid)

    for sr in step_results:
        for iid in sr.input_artifacts:
            if iid != "seed" and iid not in produced_artifacts:
                all_errors.append("missing producer for artifact_id: " + iid)

    if duplicate_step_ids:
        topo_order = []
    else:
        topo_order, topo_errors = _topological_sort(step_results)
        if topo_errors:
            all_errors.extend(topo_errors)

    ok = len(all_errors) == 0 and all(sr.valid for sr in step_results)

    return PackageResult(
        ok=ok,
        step_order=list(topo_order),
        steps=step_results,
        errors=all_errors,
    )


def render_workflow_package_markdown(result):
    status_str = "VALID" if result.ok else "INVALID"
    lines = [
        "# Workflow Package Report",
        "",
        "**Status:** " + status_str,
        "",
        "## Step Order",
        "",
    ]
    if result.step_order:
        for idx, sid in enumerate(result.step_order, 1):
            lines.append(str(idx) + ". `" + sid + "`")
    else:
        lines.append("_No valid deterministic order could be computed._")

    lines.extend(["", "## Per-Step Findings", ""])
    if not result.steps:
        lines.append("_No steps loaded._")
    for sr in result.steps:
        status = "OK" if sr.valid else "ERRORS"
        lines.append("### `" + sr.step_id + "` (" + status + ")")
        lines.append("")
        if sr.input_artifacts:
            inputs_str = ", ".join("`" + i + "`" for i in sr.input_artifacts)
            lines.append("**Inputs:** " + inputs_str)
            lines.append("")
        if sr.output_artifacts:
            outputs_str = ", ".join("`" + o + "`" for o in sr.output_artifacts)
            lines.append("**Outputs:** " + outputs_str)
            lines.append("")
        if sr.errors:
            lines.append("**Errors:**")
            for err in sr.errors:
                lines.append("- " + err)
            lines.append("")

    if result.errors:
        lines.extend(["## Aggregate Errors", ""])
        for err in result.errors:
            lines.append("- " + err)
        lines.append("")

    return "\n".join(lines)


def _topological_sort(step_results):
    errors = []
    all_step_ids = [sr.step_id for sr in step_results]
    id_set = set(all_step_ids)

    producer_map = {}
    seen_producer = set()
    for sr in step_results:
        for oid in sr.output_artifacts:
            if oid not in seen_producer:
                producer_map[oid] = sr.step_id
                seen_producer.add(oid)

    adj = defaultdict(list)
    in_degree = {sid: 0 for sid in all_step_ids}

    for sr in step_results:
        for iid in sr.input_artifacts:
            if iid == "seed":
                continue
            if iid not in producer_map:
                continue
            dep = producer_map[iid]
            if dep != sr.step_id and sr.step_id not in adj.get(dep, []):
                adj[dep].append(sr.step_id)
                in_degree[sr.step_id] += 1

    queue = sorted([sid for sid, deg in in_degree.items() if deg == 0])
    order = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        neighbours = sorted(adj.get(node, []))
        for nb in neighbours:
            in_degree[nb] -= 1
            if in_degree[nb] == 0:
                inserted = False
                for i, q_item in enumerate(queue):
                    if nb < q_item:
                        queue.insert(i, nb)
                        inserted = True
                        break
                if not inserted:
                    queue.append(nb)

    if len(order) != len(all_step_ids):
        errors.append("workflow package contains a cycle")

    return order, errors
