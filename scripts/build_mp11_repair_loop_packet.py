"""Build ignored P52 MP11 self-audit and repair-loop tickets.

The script reads sanitized tracked sample metadata plus the ignored source
excerpt packet in agent-delegation-lab. It writes ignored worker tickets and
Agent Workbench eval manifests under the target project's runtime tree.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_SAMPLE = Path(
    "benchmarks/mp11_document_metadata_index/audit_calibration_01/"
    "qwen_x16_audit_sample.json"
)
DEFAULT_AUDIT_PACKET = Path(
    "runtime/mp11_document_metadata_index/audit_calibration_01/"
    "qwen_x16_audit_packet.md"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--agent-workbench-root", type=Path, default=Path("."))
    parser.add_argument("--model", default="gpt-oss:120b")
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument(
        "--self-audit-result",
        type=Path,
        default=None,
        help="Optional ignored probe result used to build the repair-run ticket.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runtime/agent_workbench/p52_mp11_repair_loop_01"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    workbench_root = args.agent_workbench_root.resolve()
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_path = project_root / DEFAULT_SAMPLE
    audit_packet_path = project_root / DEFAULT_AUDIT_PACKET
    sample = json.loads(sample_path.read_text(encoding="utf-8-sig"))
    audit_packet = audit_packet_path.read_text(encoding="utf-8-sig")
    record_count = len(sample.get("records", []))

    self_audit_ticket = output_dir / "mp11-qwen-x16-self-audit.ticket.md"
    repair_ticket = output_dir / (
        "mp11-qwen-x16-repair-with-self-audit.ticket.md"
        if args.self_audit_result
        else "mp11-qwen-x16-repair.ticket.md"
    )
    self_audit_manifest = output_dir / "mp11-qwen-x16-self-audit.manifest.json"
    repair_manifest = output_dir / "mp11-qwen-x16-repair.manifest.json"

    self_audit_ticket.write_text(
        build_self_audit_ticket(sample, audit_packet, args.model),
        encoding="utf-8",
    )
    repair_ticket.write_text(
        build_repair_ticket(
            sample,
            self_audit_ticket,
            args.model,
            audit_packet=(
                audit_packet if args.self_audit_result is not None else None
            ),
            self_audit_output=(
                extract_assistant_message(args.self_audit_result)
                if args.self_audit_result is not None
                else None
            ),
        ),
        encoding="utf-8",
    )
    write_manifest(
        self_audit_manifest,
        evaluation_id="p52_mp11_qwen_x16_self_audit",
        ticket=self_audit_ticket.relative_to(project_root),
        output_dir=(output_dir / "self_audit_eval").relative_to(project_root),
        model=args.model,
        timeout_seconds=args.timeout_seconds,
        workbench_root=workbench_root,
        base_directory=(output_dir / "copilot_sdk_home_self_audit").relative_to(
            project_root
        ),
    )
    write_manifest(
        repair_manifest,
        evaluation_id="p52_mp11_qwen_x16_repair",
        ticket=repair_ticket.relative_to(project_root),
        output_dir=(output_dir / "repair_eval").relative_to(project_root),
        model=args.model,
        timeout_seconds=args.timeout_seconds,
        workbench_root=workbench_root,
        base_directory=(output_dir / "copilot_sdk_home_repair").relative_to(
            project_root
        ),
    )

    summary = {
        "schema_version": 1,
        "packet_id": "p52_mp11_repair_loop_01",
        "project_root_recorded": False,
        "source_sample": str(DEFAULT_SAMPLE).replace("\\", "/"),
        "source_audit_packet": str(DEFAULT_AUDIT_PACKET).replace("\\", "/"),
        "raw_source_excerpt_tracked": False,
        "record_count": record_count,
        "model": args.model,
        "tickets": {
            "self_audit": str(self_audit_ticket.relative_to(project_root)).replace(
                "\\", "/"
            ),
            "repair": str(repair_ticket.relative_to(project_root)).replace("\\", "/"),
        },
        "manifests": {
            "self_audit": str(
                self_audit_manifest.relative_to(project_root)
            ).replace("\\", "/"),
            "repair": str(repair_manifest.relative_to(project_root)).replace(
                "\\", "/"
            ),
        },
    }
    (output_dir / "packet_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


def build_self_audit_ticket(sample: dict, audit_packet: str, model: str) -> str:
    return "\n".join(
        [
            "# P52 MP11 Local Self-Audit Ticket",
            "",
            "Use the local self-audit contract from "
            "`templates/local_self_audit_ticket.md`.",
            "",
            "Return JSONL only. Do not include Markdown fences or prose.",
            "",
            "Current state:",
            "",
            f"- source_sample_id: `{sample.get('sample_id', '')}`",
            f"- source_experiment: `{sample.get('source_experiment', '')}`",
            f"- candidate_record_count: {len(sample.get('records', []))}",
            f"- worker_model: `{model}`",
            "",
            "Audit labels:",
            "",
            "- `accepted_candidate`",
            "- `needs_repair`",
            "- `likely_reject`",
            "",
            "Required JSONL fields:",
            "",
            "- `candidate_record_id`",
            "- `draft_label`",
            "- `defect_categories`",
            "- `supported_by_excerpt`",
            "- `page_anchor_ok`",
            "- `object_type_ok`",
            "- `title_ok`",
            "- `summary_ok`",
            "- `repair_instruction`",
            "- `evidence_quote`",
            "- `rationale`",
            "- `worker_model`",
            "",
            "Do not claim final validation. The supervisor owns final labels.",
            "",
            "## Candidate Packet",
            "",
            audit_packet,
            "",
        ]
    )


def build_repair_ticket(
    sample: dict,
    self_audit_ticket: Path,
    model: str,
    *,
    audit_packet: str | None = None,
    self_audit_output: str | None = None,
) -> str:
    lines = [
        "# P52 MP11 Delegated Repair Ticket",
        "",
        "Use the delegated repair contract from "
        "`templates/delegated_repair_iteration_ticket.md`.",
        "",
        "Return JSONL only. Do not include Markdown fences or prose.",
        "",
        "Current state:",
        "",
        f"- source_sample_id: `{sample.get('sample_id', '')}`",
        f"- source_experiment: `{sample.get('source_experiment', '')}`",
        f"- candidate_record_count: {len(sample.get('records', []))}",
        f"- worker_model: `{model}`",
        "",
        "Required JSONL fields:",
        "",
        "- `candidate_record_id`",
        "- `repair_action`",
        "- `repaired_object_type`",
        "- `repaired_title`",
        "- `repaired_section_path`",
        "- `repaired_summary`",
        "- `source_quote`",
        "- `remaining_defects`",
        "- `ready_for_supervisor_delta_review`",
        "- `rationale`",
        "- `worker_model`",
        "",
        "Self-audit source ticket:",
        "",
        f"- `{self_audit_ticket}`",
        "",
    ]
    if self_audit_output is None or audit_packet is None:
        lines.extend(
            [
                "The self-audit output must be appended by the supervisor after "
                "the self-audit run. Until then this ticket is a reproducible "
                "repair template.",
                "",
                "Supervisor must append the self-audit JSONL plus the candidate "
                "packet before running this repair ticket.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "Repair rules:",
            "",
            "- Use candidate identifiers from the original candidate packet.",
            "- If a self-audit identifier does not match the original candidate "
            "identifier, mark the matching repair action as `unrepairable` with "
            "`remaining_defects` set to `needs_supervisor_judgment`.",
            "- If self-audit says a candidate is supported, return "
            "`unchanged_supported` only when the original sample identifier is "
            "preserved.",
            "- Do not claim final validation.",
            "",
            "## Self-Audit JSONL",
            "",
            "```jsonl",
            self_audit_output.strip(),
            "```",
            "",
            "## Candidate Packet",
            "",
            audit_packet,
            "",
        ]
    )
    return "\n".join(
        lines
    )


def extract_assistant_message(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    marker = "## Assistant Messages"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"assistant message section not found: {path}")
    start += len(marker)
    end = text.find("## Raw Event Records", start)
    if end < 0:
        end = len(text)
    message = text[start:end].strip()
    if not message:
        raise ValueError(f"assistant message section is empty: {path}")
    return message


def write_manifest(
    path: Path,
    *,
    evaluation_id: str,
    ticket: Path,
    output_dir: Path,
    model: str,
    timeout_seconds: int,
    workbench_root: Path,
    base_directory: Path,
) -> None:
    data = {
        "evaluation_id": evaluation_id,
        "ticket": str(ticket).replace("\\", "/"),
        "expected_marker": "",
        "required_sections": [],
        "forbidden_phrases": [
            "would have",
            "raw prompt",
            "provider URL",
            "Authorization",
            "Bearer",
            "final validation"
        ],
        "allow_unexpected_sections": False,
        "allow_preamble": False,
        "require_patch": False,
        "allowed_patch_files": [],
        "models": [model],
        "repeats": 1,
        "timeout_seconds": timeout_seconds,
        "output_dir": str(output_dir).replace("\\", "/"),
        "probe_script": str(
            (workbench_root / "scripts/copilot_sdk_ollama_probe.py").resolve()
        ),
        "python_executable": str(
            (workbench_root / ".venv/Scripts/python.exe").resolve()
        ),
        "base_url": "",
        "base_url_file": str(
            (workbench_root / "runtime/ollama_openai_base_url.txt").resolve()
        ),
        "provider_headers_file": str(
            (workbench_root / "runtime/local_provider_headers.json").resolve()
        ),
        "wire_api": "completions",
        "mode": "empty",
        "base_directory": str(base_directory).replace("\\", "/"),
        "sdk_source": ""
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
