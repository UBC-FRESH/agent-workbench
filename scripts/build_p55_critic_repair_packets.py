"""Build P55 Wave 9 critic and repair packets.

Wave 9 tests a local rescue lane for malformed verifier output:

1. DeepSeek-R1 acts as a validation critic and writes repair instructions.
2. Qwen3-Coder-Next acts as a repair executor and emits strict verifier JSON.

The tickets include raw failed output, candidate values, quotes, and source
chunks, so they remain under ignored ``runtime/`` paths. Tracked packet indexes
contain only sanitized metadata.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME_ROOT = Path("runtime/document_library/tsa23_tsr/p55")
DEFAULT_DEEPSEEK_PACKET = Path(
    "benchmarks/document_library/tsa23_tsr/p55_wave8_verifier_packet.json"
)
DEFAULT_FAILED_SUMMARY = (
    DEFAULT_RUNTIME_ROOT
    / "eval/wave8_disagreement_verification__tsa23_2012_23ts13ra__deepseek-r1/summary.json"
)
DEFAULT_CRITIC_INDEX = Path("benchmarks/document_library/tsa23_tsr/p55_wave9_critic_packet.json")
DEFAULT_REPAIR_INDEX = Path("benchmarks/document_library/tsa23_tsr/p55_wave9_repair_packet.json")
DEFAULT_CRITIC_MODEL = "deepseek-r1:latest"
DEFAULT_REPAIR_MODEL = "qwen3-coder-next:latest"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build P55 Wave 9 critic/repair packets.")
    parser.add_argument("stage", choices=["critic", "repair"])
    parser.add_argument("--wave8-packet", type=Path, default=DEFAULT_DEEPSEEK_PACKET)
    parser.add_argument("--failed-summary", type=Path, default=DEFAULT_FAILED_SUMMARY)
    parser.add_argument("--critic-index", type=Path, default=DEFAULT_CRITIC_INDEX)
    parser.add_argument("--repair-index", type=Path, default=DEFAULT_REPAIR_INDEX)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--critic-model", default=DEFAULT_CRITIC_MODEL)
    parser.add_argument("--repair-model", default=DEFAULT_REPAIR_MODEL)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--base-url-file", default="runtime/ollama_openai_base_url.txt")
    parser.add_argument("--provider-headers-file", default="runtime/local_provider_headers.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.stage == "critic":
        build_critic(args)
    else:
        build_repair(args)
    return 0


def build_critic(args: argparse.Namespace) -> None:
    wave8_packet = load_json(args.wave8_packet)
    failed_summary = load_json(args.failed_summary)
    failed_output = failed_summary["rows"][0]["assistant_message"]
    packet_id = f"wave9_validation_critic__{wave8_packet['document_id']}__{slug(args.critic_model)}"
    ticket_path = args.runtime_root / "tickets" / f"{packet_id}.ticket.md"
    manifest_path = args.runtime_root / "manifests" / f"{packet_id}.manifest.json"
    output_dir = args.runtime_root / "eval" / packet_id
    ticket = render_critic_ticket(wave8_packet, failed_output)
    write_text(ticket_path, ticket)
    write_json(
        manifest_path,
        manifest_payload(
            packet_id=packet_id,
            ticket_path=ticket_path,
            output_dir=output_dir,
            model=args.critic_model,
            timeout_seconds=args.timeout_seconds,
            base_url_file=args.base_url_file,
            provider_headers_file=args.provider_headers_file,
        ),
    )
    write_json(
        args.critic_index,
        {
            "schema_version": 1,
            "generated_utc": now_utc(),
            "phase": "P55",
            "wave_id": "wave9_validation_critic",
            "packet_id": packet_id,
            "document_id": wave8_packet["document_id"],
            "source_packet_id": wave8_packet["packet_id"],
            "critic_model": args.critic_model,
            "field_count": len(wave8_packet["fields"]),
            "fields": wave8_packet["fields"],
            "ticket_path": slash_path(ticket_path),
            "manifest_path": slash_path(manifest_path),
            "output_dir": slash_path(output_dir),
            "raw_ticket_policy": "Critic ticket includes failed output and schema details; keep ignored under runtime/.",
            "tracked_output_policy": "Track only sanitized critic and repair metrics.",
        },
    )
    print(f"wrote {ticket_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {args.critic_index}")


def build_repair(args: argparse.Namespace) -> None:
    wave8_packet = load_json(args.wave8_packet)
    failed_summary = load_json(args.failed_summary)
    critic_index = load_json(args.critic_index)
    critic_summary = load_json(Path(critic_index["output_dir"]) / "summary.json")
    failed_output = failed_summary["rows"][0]["assistant_message"]
    critic_output = critic_summary["rows"][0]["assistant_message"]
    original_ticket = Path(wave8_packet["ticket_path"]).read_text(encoding="utf-8-sig")
    packet_id = f"wave9_json_repair__{wave8_packet['document_id']}__{slug(args.repair_model)}"
    ticket_path = args.runtime_root / "tickets" / f"{packet_id}.ticket.md"
    manifest_path = args.runtime_root / "manifests" / f"{packet_id}.manifest.json"
    output_dir = args.runtime_root / "eval" / packet_id
    ticket = render_repair_ticket(wave8_packet, failed_output, critic_output, original_ticket)
    write_text(ticket_path, ticket)
    write_json(
        manifest_path,
        manifest_payload(
            packet_id=packet_id,
            ticket_path=ticket_path,
            output_dir=output_dir,
            model=args.repair_model,
            timeout_seconds=args.timeout_seconds,
            base_url_file=args.base_url_file,
            provider_headers_file=args.provider_headers_file,
        ),
    )
    write_json(
        args.repair_index,
        {
            "schema_version": 1,
            "generated_utc": now_utc(),
            "phase": "P55",
            "wave_id": "wave9_json_repair",
            "packet_id": packet_id,
            "document_id": wave8_packet["document_id"],
            "source_packet_id": wave8_packet["packet_id"],
            "critic_packet_id": critic_index["packet_id"],
            "repair_model": args.repair_model,
            "field_count": len(wave8_packet["fields"]),
            "fields": wave8_packet["fields"],
            "ticket_path": slash_path(ticket_path),
            "manifest_path": slash_path(manifest_path),
            "output_dir": slash_path(output_dir),
            "raw_ticket_policy": "Repair ticket includes failed output, critic instructions, and original verifier ticket; keep ignored under runtime/.",
            "tracked_output_policy": "Track only sanitized repair metrics.",
        },
    )
    print(f"wrote {ticket_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {args.repair_index}")


def render_critic_ticket(wave8_packet: dict[str, Any], failed_output: str) -> str:
    fields = json.dumps(wave8_packet["fields"], indent=2)
    return f"""# P55 Wave 9 Validation Critic Ticket

## Mission

Inspect a failed Wave 8 verifier response and prepare repair instructions for
a separate strict JSON repair executor. Do not produce the final repaired JSON.
Do not use tools, commands, files, browsing, or GitHub.

Return one strict JSON object only. No markdown fences, prose, or
chain-of-thought.

## Expected Verifier Contract

- The final artifact must be one JSON object.
- Top-level keys must include `verifier_model`, `review_status`,
  `document_id`, `source_packet_id`, and `verdicts`.
- `verdicts` must be an object with exactly these field keys:

```json
{fields}
```

- Each field object must include `verdict`, `final_status`, `final_value`,
  `final_units`, `final_page_anchor`, `final_chunk_id`, `source_quote`,
  `confidence`, and `reason_code`.
- `source_quote` must be 25 words or fewer.
- Verdict labels must never be used as field keys.

## Output Schema

```json
{{
  "critic_model": "<ACTIVE_MODEL_NAME>",
  "review_status": "raw_critic_candidate",
  "source_packet_id": "{wave8_packet['packet_id']}",
  "repair_target": "failed_wave8_verifier_output",
  "issues": [
    {{
      "issue_type": "wrong_field_key",
      "severity": "high",
      "field": "example_field_or_null",
      "repair_instruction": "Concrete instruction for the repair executor."
    }}
  ],
  "repair_strategy": [
    "Ordered repair step."
  ],
  "do_not_change": [
    "Facts that should be preserved if source-supported."
  ]
}}
```

## Failed Verifier Output

```text
{safe_fence_text(failed_output)}
```
"""


def render_repair_ticket(
    wave8_packet: dict[str, Any],
    failed_output: str,
    critic_output: str,
    original_ticket: str,
) -> str:
    allowed_chunk_ids = sorted(set(re.findall(r"tsa23_2012_23ts13ra::pages_\d{3}_\d{3}", original_ticket)))
    fields = {
        field: {
            "verdict": "needs_supervisor",
            "final_status": "uncertain",
            "final_value": None,
            "final_units": None,
            "final_page_anchor": None,
            "final_chunk_id": None,
            "source_quote": None,
            "confidence": 0.0,
            "reason_code": "unreviewed",
        }
        for field in wave8_packet["fields"]
    }
    top_level_skeleton = {
        "verifier_model": "<ACTIVE_MODEL_NAME>",
        "review_status": "raw_verifier_candidate",
        "document_id": wave8_packet["document_id"],
        "source_packet_id": wave8_packet["source_packet_id"],
        "verdicts": fields,
    }
    return f"""# P55 Wave 9 Strict JSON Repair Executor Ticket

## Mission

Repair the failed verifier output into one strict JSON object that satisfies
the Wave 8 verifier schema. Use the original verifier ticket and the validation
critic report as guidance. Do not use tools, commands, files, browsing, or
GitHub.

Return only the repaired JSON object. No markdown fences, prose, or
chain-of-thought.

Allowed `verdict` values are exactly:

- `left_correct`
- `right_correct`
- `both_correct_equivalent`
- `both_wrong`
- `insufficient_evidence`
- `needs_supervisor`

Do not use any other verdict labels. In particular, do not use
`supervisor_review_required`; use `needs_supervisor` instead.

Allowed `final_chunk_id` values are exactly:

{chr(10).join(f"- `{chunk_id}`" for chunk_id in allowed_chunk_ids)}

Do not use `source_supported`, page labels, reason codes, or any other value in
`final_chunk_id`. Use one of the allowed chunk IDs above, or null.

## Required Full JSON Skeleton

Fill this exact top-level object shape. Preserve the top-level keys and exactly
these `verdicts` field keys:

```json
{json.dumps(top_level_skeleton, indent=2)}
```

## Failed Verifier Output To Repair

```text
{safe_fence_text(failed_output)}
```

## Validation Critic Repair Instructions

```text
{safe_fence_text(critic_output)}
```

## Original Verifier Ticket

```text
{safe_fence_text(original_ticket)}
```
"""


def manifest_payload(
    *,
    packet_id: str,
    ticket_path: Path,
    output_dir: Path,
    model: str,
    timeout_seconds: int,
    base_url_file: str,
    provider_headers_file: str,
) -> dict[str, Any]:
    return {
        "evaluation_id": packet_id,
        "ticket": slash_path(ticket_path),
        "expected_marker": "",
        "required_sections": [],
        "forbidden_phrases": ["would do", "would have", "ready for", "completed successfully"],
        "allow_unexpected_sections": True,
        "allow_preamble": False,
        "require_patch": False,
        "allowed_patch_files": [],
        "models": [model],
        "repeats": 1,
        "timeout_seconds": timeout_seconds,
        "output_dir": slash_path(output_dir),
        "probe_script": "scripts/copilot_sdk_ollama_probe.py",
        "python_executable": "",
        "base_url": "",
        "base_url_file": base_url_file,
        "provider_headers_file": provider_headers_file,
        "wire_api": "completions",
        "mode": "empty",
        "base_directory": slash_path(output_dir.parent / f"copilot_sdk_home_{slug(packet_id)}"),
        "sdk_source": "",
    }


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slash_path(path: Path) -> str:
    return path.as_posix()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def safe_fence_text(value: str) -> str:
    return value.replace("```", "~~~")


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
