"""Validate the public-safe P113.1 one-tool adapter fixture contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import PurePosixPath, Path


DEFAULT_FIXTURE = Path("benchmarks/p113_function_tool_adapter/adapter_contract_fixtures.json")
REQUIRED_CASES = {
    "valid_translation",
    "one_call_limit",
    "allowed_root_containment",
    "malformed_provider_output",
    "history_round_trip",
    "output_only_history",
}


def patch_paths(patch: str) -> list[str]:
    return re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", patch, flags=re.MULTILINE)


def well_formed_patch(patch: str) -> bool:
    return (
        patch.startswith("*** Begin Patch\n")
        and patch.rstrip().endswith("*** End Patch")
        and bool(patch_paths(patch))
    )


def contained(path: str, allowed_root: str) -> bool:
    candidate = PurePosixPath(path)
    root = PurePosixPath(allowed_root)
    if not path or path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", path):
        return False
    if ".." in candidate.parts:
        return False
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["fixture must be a JSON object"]
    if data.get("contract_id") != "p113_apply_patch_function_adapter_v1":
        errors.append("unexpected contract_id")
    root = data.get("allowed_root")
    if not isinstance(root, str) or not root:
        errors.append("allowed_root must be a non-empty string")
        root = ""
    tool = data.get("tool")
    if not isinstance(tool, dict) or tool.get("type") != "function" or tool.get("name") != "apply_patch":
        errors.append("tool must be the apply_patch function")
    elif tool.get("strict") is not True or tool.get("parameters", {}).get("required") != ["patch"] or tool["parameters"].get("additionalProperties") is not False:
        errors.append("tool must require only strict patch arguments")
    cases = data.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be a list"]
    by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
    if set(by_id) != REQUIRED_CASES:
        errors.append("fixtures must contain exactly the required case identifiers")
    for case_id, case in by_id.items():
        calls = case.get("provider_calls")
        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{case_id}: missing calls or expected result")
            continue
        if case_id == "output_only_history":
            history = case.get("custom_history")
            if not isinstance(history, list) or len(history) != 1 or not isinstance(history[0], dict) or history[0].get("type") != "custom_tool_call_output":
                errors.append("output_only_history must provide exactly one custom output")
            elif history[0].get("call_id") != expected.get("requires_prior_validated_call_id"):
                errors.append("output_only_history must require its prior validated call ID")
            if expected.get("function_history_types") != ["function_call_output"] or expected.get("tool_choice") != "none" or expected.get("tools") != []:
                errors.append("output_only_history must disable follow-up tools")
            continue
        if not isinstance(calls, list):
            errors.append(f"{case_id}: missing calls or expected result")
            continue
        for call in calls:
            if not isinstance(call, dict) or call.get("name") != "apply_patch":
                errors.append(f"{case_id}: provider call must name apply_patch")
                continue
            try:
                arguments = json.loads(call.get("arguments", ""))
            except (TypeError, json.JSONDecodeError):
                arguments = None
            if case_id in {"valid_translation", "one_call_limit", "allowed_root_containment", "history_round_trip"}:
                if not isinstance(arguments, dict) or set(arguments) != {"patch"} or not isinstance(arguments["patch"], str):
                    errors.append(f"{case_id}: expected a patch-only JSON argument")
                elif not well_formed_patch(arguments["patch"]):
                    errors.append(f"{case_id}: patch must have one supported complete envelope")
                elif case_id != "allowed_root_containment" and any(not contained(path, root) for path in patch_paths(arguments["patch"])):
                    errors.append(f"{case_id}: valid patch path escapes allowed_root")
        if case_id == "valid_translation":
            event = expected.get("custom_event")
            if expected.get("status") != "accept" or not isinstance(event, dict) or any(event.get(key) != calls[0].get(key) for key in ("id", "call_id", "name")):
                errors.append("valid_translation must preserve provider event identity")
        if case_id == "one_call_limit" and (len(calls) != 2 or expected.get("code") != "call_limit_exceeded"):
            errors.append("one_call_limit must prove exactly two calls and rejection")
        if case_id == "allowed_root_containment" and expected.get("code") != "path_outside_allowed_root":
            errors.append("allowed_root_containment must reject with containment code")
        if case_id == "malformed_provider_output" and expected.get("code") != "malformed_provider_call":
            errors.append("malformed_provider_output must reject malformed calls")
        if case_id == "history_round_trip":
            history = case.get("custom_history")
            if not isinstance(history, list) or [item.get("type") for item in history if isinstance(item, dict)] != ["custom_tool_call", "custom_tool_call_output"]:
                errors.append("history_round_trip must provide one call/output custom history pair")
            elif history[0].get("call_id") != history[1].get("call_id") or history[0].get("id") != calls[0].get("id") or history[0].get("input") != json.loads(calls[0]["arguments"])["patch"]:
                errors.append("history_round_trip must preserve event identity")
            if expected.get("function_history_types") != ["function_call", "function_call_output"] or expected.get("tool_choice") != "none" or expected.get("tools") != []:
                errors.append("history_round_trip must disable follow-up tools")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    args = parser.parse_args()
    try:
        data = json.loads(args.fixture.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"p113 adapter fixture contract: invalid ({exc})")
        return 1
    errors = validate(data)
    if errors:
        print("p113 adapter fixture contract: invalid")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("p113 adapter fixture contract: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
