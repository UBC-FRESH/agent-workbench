#!/usr/bin/env python3
"""Multi-turn tool-loop conformance probe for an OpenAI-compatible endpoint.

A single tool call proves the parser emits one call. It does not prove the loop
works. This probe forces two *dependent* calls: the second tool requires an
identifier that only appears in the first tool's result, so a model that
fabricates instead of reading the tool result will fail visibly.

Checks, in order:
  1. round 1 returns finish_reason=tool_calls with well-formed JSON arguments
  2. round 2 issues a different tool call using the value returned by round 1
  3. round 3 produces a final answer containing facts from the tool results
"""
import argparse
import json
import sys
import urllib.request

SECRET_USER_ID = "u-7734-zx"       # only obtainable from tool result
SECRET_ORDER = "ORD-91442"          # only obtainable from tool result

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_user",
            "description": "Look up a user's internal id by their display name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_orders",
            "description": "List order ids for an internal user id.",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"],
            },
        },
    },
]


def call(url, model, messages, timeout=300):
    body = {
        "model": model,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": 0.2,
        "max_tokens": 512,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def run_tool(name, args):
    if name == "lookup_user":
        return {"user_id": SECRET_USER_ID}
    if name == "list_orders":
        if args.get("user_id") != SECRET_USER_ID:
            return {"error": f"unknown user_id {args.get('user_id')!r}"}
        return {"orders": [SECRET_ORDER]}
    return {"error": f"no such tool {name}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--max-rounds", type=int, default=5)
    args = ap.parse_args()

    messages = [{
        "role": "user",
        "content": ("Find the order ids belonging to the user named Alice. "
                    "First look up her internal user id, then list her orders. "
                    "Use the provided tools; do not guess identifiers."),
    }]

    failures = []
    used_user_id_from_tool = False
    tools_called = []

    for rnd in range(1, args.max_rounds + 1):
        data = call(args.url, args.model, messages)
        choice = data["choices"][0]
        msg = choice["message"]
        finish = choice.get("finish_reason")
        calls = msg.get("tool_calls") or []
        print(f"--- round {rnd}: finish_reason={finish} tool_calls={len(calls)}")

        if not calls:
            content = (msg.get("content") or "").strip()
            print(f"    final content: {content[:300]}")
            if SECRET_ORDER in content:
                print("    PASS: final answer contains the tool-supplied order id")
            else:
                failures.append("final answer missing tool-supplied order id")
            break

        messages.append({
            "role": "assistant",
            "content": msg.get("content") or "",
            "tool_calls": calls,
        })
        for tc in calls:
            fn = tc["function"]
            name = fn["name"]
            try:
                parsed = json.loads(fn["arguments"] or "{}")
            except json.JSONDecodeError as exc:
                failures.append(f"round {rnd}: arguments not valid JSON: {exc}")
                parsed = {}
            tools_called.append(name)
            print(f"    call: {name}({json.dumps(parsed)})")
            if name == "list_orders" and parsed.get("user_id") == SECRET_USER_ID:
                used_user_id_from_tool = True
            result = run_tool(name, parsed)
            if "error" in result:
                failures.append(f"round {rnd}: {name} got bad args -> {result['error']}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", f"call_{rnd}"),
                "content": json.dumps(result),
            })
    else:
        failures.append("loop did not terminate within max rounds")

    print("\n=== summary ===")
    print(f"tools called in order: {tools_called}")
    print(f"second call used id from first tool result: {used_user_id_from_tool}")
    if not used_user_id_from_tool:
        failures.append("second tool call did not use the id returned by the first")
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("RESULT: PASS (multi-turn dependent tool loop works)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
