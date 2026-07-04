"""Comparison reports for same-ticket worker evaluation summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_eval_summary(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("eval summary must be a JSON object")
    if "runs" not in data and "rows" not in data:
        raise ValueError("eval summary must contain runs or rows")
    if "classification_counts" not in data:
        raise ValueError("eval summary must contain classification_counts")
    return data


def render_eval_comparison(paths: list[Path]) -> str:
    summaries = [(path, load_eval_summary(path)) for path in paths]
    lines = [
        "# Eval Comparison Report",
        "",
        "This report compares existing same-ticket evaluation summaries. Conclusions",
        "are scoped to the supplied ticket family, models, repeats, and summaries.",
        "It is not a broad model ranking.",
        "",
        "## Inputs",
        "",
    ]
    for path, summary in summaries:
        lines.append(
            "- `{path}`: `{evaluation_id}` ({models} model(s), {repeats} repeat(s))".format(
                path=path.as_posix(),
                evaluation_id=summary.get("evaluation_id", ""),
                models=len(summary.get("models", [])),
                repeats=summary.get("repeats", ""),
            )
        )

    lines.extend(
        [
            "",
            "## Classification Counts",
            "",
            "| Evaluation | Model | Classification | Count |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for _path, summary in summaries:
        evaluation_id = summary.get("evaluation_id", "")
        counts = summary.get("classification_counts", {})
        if isinstance(counts, dict):
            for model, model_counts in sorted(counts.items()):
                if isinstance(model_counts, dict):
                    for classification, count in sorted(model_counts.items()):
                        lines.append(
                            f"| {evaluation_id} | `{model}` | `{classification}` | {count} |"
                        )

    lines.extend(
        [
            "",
            "## Consistency By Model",
            "",
            "| Evaluation | Model | Repeats | Classifications | Consistency |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for _path, summary in summaries:
        evaluation_id = summary.get("evaluation_id", "")
        runs = summary_runs(summary)
        by_model: dict[str, list[str]] = {}
        if isinstance(runs, list):
            for run in runs:
                if isinstance(run, dict):
                    model = str(run.get("model", ""))
                    classification = str(run.get("classification", ""))
                    by_model.setdefault(model, []).append(classification)
        for model, classifications in sorted(by_model.items()):
            distinct = sorted(set(classifications))
            consistency = "stable" if len(distinct) == 1 else "variable"
            lines.append(
                "| {evaluation} | `{model}` | {repeats} | {classes} | `{consistency}` |".format(
                    evaluation=evaluation_id,
                    model=model,
                    repeats=len(classifications),
                    classes=", ".join(f"`{item}`" for item in distinct),
                    consistency=consistency,
                )
            )

    lines.extend(
        [
            "",
            "## Per-Run Outcomes",
            "",
            "| Evaluation | Model | Repeat | Status | Blocker | Classification | Result File |",
            "| --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for _path, summary in summaries:
        evaluation_id = summary.get("evaluation_id", "")
        runs = summary_runs(summary)
        if isinstance(runs, list):
            for run in runs:
                if isinstance(run, dict):
                    lines.append(
                        "| {evaluation} | `{model}` | {repeat} | `{status}` | `{blocker}` | "
                        "`{classification}` | `{result_file}` |".format(
                            evaluation=evaluation_id,
                            model=run.get("model", ""),
                            repeat=run.get("repeat_index", ""),
                            status=run.get("status", ""),
                            blocker=run.get("blocker", ""),
                            classification=run.get("classification", ""),
                            result_file=run.get("result_file", ""),
                        )
                    )

    lines.extend(
        [
            "",
            "## Supervisor Use",
            "",
            "- Treat stable classifications as evidence about this exact ticket family only.",
            "- Treat variable classifications as a prompt for repeat runs or narrower tickets.",
            "- Do not promote broad model rankings from this report.",
            "",
        ]
    )
    return "\n".join(lines)


def summary_runs(summary: dict[str, Any]) -> list[Any]:
    runs = summary.get("runs", summary.get("rows", []))
    return runs if isinstance(runs, list) else []
