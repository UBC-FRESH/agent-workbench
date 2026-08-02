#!/usr/bin/env python3
"""Agent-path conformance probe: streaming tool calls, parallel calls, schema.

Prior probes covered non-streaming tool calls and streaming without tools. Real
editor clients do both at once, which is a distinct code path: tool calls arrive
as incremental deltas that must be reassembled across chunks. A parser that
handles complete responses can still emit split arguments or truncated names
when streamed.

Tests:
  A. streaming + tools  -- reassemble deltas, require valid JSON arguments
  B. parallel calls     -- two independent calls in one assistant turn
  C. structured output  -- response_format json_schema returns conforming JSON
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

WEATHER_TOOL = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current temperature for one city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "unit": {"type": "string", "enum": ["c", "f"]},
            },
            "required": ["city"],
        },
    },
}]

REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "city": {"type": "string"},
        "temperature_c": {"type": "number"},
        "conditions": {"type": "string"},
    },
    "required": ["city", "temperature_c", "conditions"],
    "additionalProperties": False,
}


def post(url, body, timeout=300, stream=False):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from None
    if stream:
        return resp
    with resp:
        return json.load(resp)


def stream_tool_calls(url, model, messages, tools):
    """Reassemble streamed tool-call deltas keyed by index."""
    body = {
        "model": model, "messages": messages, "tools": tools,
        "tool_choice": "auto", "stream": True, "temperature": 0.2,
        "max_tokens": 512, "chat_template_kwargs": {"enable_thinking": False},
    }
    acc = {}
    finish = None
    chunks = 0
    with post(url, body, stream=True) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            obj = json.loads(payload)
            for ch in obj.get("choices") or []:
                if ch.get("finish_reason"):
                    finish = ch["finish_reason"]
                for tc in (ch.get("delta") or {}).get("tool_calls") or []:
                    idx = tc.get("index", 0)
                    slot = acc.setdefault(idx, {"name": "", "arguments": ""})
                    fn = tc.get("function") or {}
                    if fn.get("name"):
                        slot["name"] += fn["name"]
                    if fn.get("arguments"):
                        slot["arguments"] += fn["arguments"]
                        chunks += 1
    return finish, [acc[k] for k in sorted(acc)], chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--model", required=True)
    args = ap.parse_args()
    failures = []

    # --- A: streaming + tools -------------------------------------------
    print("=== A. streaming + tool calls ===")
    try:
        finish, calls, chunks = stream_tool_calls(
            args.url, args.model,
            [{"role": "user", "content": "What is the temperature in Vancouver? Use the tool."}],
            WEATHER_TOOL)
        print(f"  finish_reason={finish} calls={len(calls)} arg_deltas={chunks}")
        if finish != "tool_calls":
            failures.append(f"A: finish_reason was {finish!r}, expected 'tool_calls'")
        if not calls:
            failures.append("A: no tool calls reassembled from stream")
        for c in calls:
            print(f"  call: {c['name']}({c['arguments']})")
            if not c["name"]:
                failures.append("A: tool name empty after reassembly")
            try:
                json.loads(c["arguments"] or "{}")
            except json.JSONDecodeError as exc:
                failures.append(f"A: streamed arguments not valid JSON: {exc}")
        if chunks > 1:
            print("  (arguments genuinely arrived split across deltas)")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"A: {type(exc).__name__}: {exc}")

    # --- B: parallel tool calls -----------------------------------------
    print("\n=== B. parallel tool calls in one turn ===")
    try:
        finish, calls, _ = stream_tool_calls(
            args.url, args.model,
            [{"role": "user", "content": (
                "Get the current temperature for BOTH Vancouver and Montreal. "
                "Issue both tool calls together in one turn.")}],
            WEATHER_TOOL)
        cities = []
        for c in calls:
            try:
                cities.append(json.loads(c["arguments"] or "{}").get("city"))
            except json.JSONDecodeError:
                failures.append("B: arguments not valid JSON")
        print(f"  finish_reason={finish} calls={len(calls)} cities={cities}")
        if len(calls) < 2:
            print("  NOTE: model issued calls sequentially rather than in parallel")
        else:
            print("  PASS: two calls in a single assistant turn")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"B: {type(exc).__name__}: {exc}")

    # --- C: structured output -------------------------------------------
    print("\n=== C. structured output (json_schema) ===")
    try:
        data = post(args.url, {
            "model": args.model,
            "messages": [{"role": "user", "content":
                          "Report the weather for Vancouver: 14 degrees C, light rain."}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "weather_report",
                                "schema": REPORT_SCHEMA, "strict": True},
            },
            "temperature": 0.2, "max_tokens": 256,
            "chat_template_kwargs": {"enable_thinking": False},
        })
        content = data["choices"][0]["message"]["content"]
        print(f"  raw: {content[:200]}")
        parsed = json.loads(content)
        missing = [k for k in REPORT_SCHEMA["required"] if k not in parsed]
        extra = [k for k in parsed if k not in REPORT_SCHEMA["properties"]]
        if missing:
            failures.append(f"C: missing required keys {missing}")
        if extra:
            failures.append(f"C: additionalProperties violated: {extra}")
        if not missing and not extra:
            print("  PASS: output parsed and conforms to schema")
    except json.JSONDecodeError as exc:
        failures.append(f"C: response was not valid JSON: {exc}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"C: {type(exc).__name__}: {exc}")

    print("\n=== summary ===")
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
