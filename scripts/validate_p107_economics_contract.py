"""Offline validation for the first P107 configuration-research contracts."""
from __future__ import annotations
import json
import sys
from pathlib import Path

EXPECTED = {
    "C0": ("coordinator_only", True, False, None),
    "C1": ("flat_worker", False, False, "gpt_luna_worker"),
    "C2": ("flat_supervisor_worker", False, False, "gpt_luna_worker"),
    "C3": ("nested_supervisor_worker", False, True, "gpt_luna_worker"),
    "C4": ("flat_supervisor_ollama_worker", False, False, "ollama_qwen_coder_worker"),
}

def validate(path: str | Path) -> list[str]:
    data=json.loads(Path(path).read_text(encoding="utf-8")); errors=[]
    if data.get("schema_version")!="p107_configuration_registry_v1": errors.append("bad schema version")
    rows={x.get("id"):x for x in data.get("configurations",[]) if isinstance(x,dict)}
    for key, expected in EXPECTED.items():
        row=rows.get(key)
        if not row: errors.append(f"missing {key}"); continue
        for field, value in zip(("topology","coordinator_implementation_allowed","supervisor_may_spawn","worker"),expected):
            if row.get(field)!=value: errors.append(f"{key}.{field} must be {value!r}")
    policy=data.get("advisor_policy",{})
    if policy.get("hard_wait") is not True: errors.append("Advisor hard wait required")
    if policy.get("fresh_session_per_run") is not True: errors.append("fresh Advisor session per run required")
    if policy.get("reuse_with_send_input") is not True: errors.append("persistent Advisor reuse required")
    if policy.get("max_completed_reviews")!=3: errors.append("exactly three Advisor reviews required")
    if policy.get("initial_packet_max_estimated_tokens") != 16000: errors.append("initial Advisor packet cap must be 16000 tokens")
    if policy.get("repair_delta_max_estimated_tokens") != 4000: errors.append("Advisor repair delta cap must be 4000 tokens")
    return errors

if __name__=="__main__":
    errors=validate(sys.argv[1])
    if errors: print("\n".join(errors)); raise SystemExit(1)
    print("P107 configuration registry valid")
