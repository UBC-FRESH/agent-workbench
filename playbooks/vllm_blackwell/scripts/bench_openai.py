#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


PROMPTS = [
    "Write a concise Python function that batches an iterable into lists of size n.",
    "Explain the performance tradeoffs between KV cache size and long context inference.",
    "Given a failing unit test, outline a careful debugging workflow for a large codebase.",
]


def post_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def stream_chat(
    base_url: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
) -> dict[str, float | int | None]:
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "stream": True,
                "stream_options": {"include_usage": True},
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()
    first_token_at: float | None = None
    chunks = 0
    output_parts: list[str] = []
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    with urllib.request.urlopen(request, timeout=300) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data: "):
                continue
            data = line.removeprefix("data: ")
            if data == "[DONE]":
                break
            event = json.loads(data)
            usage = event.get("usage")
            if usage:
                prompt_tokens = usage.get("prompt_tokens")
                completion_tokens = usage.get("completion_tokens")
                total_tokens = usage.get("total_tokens")
            choices = event.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            content = delta.get("content")
            if content:
                if first_token_at is None:
                    first_token_at = time.perf_counter()
                chunks += 1
                output_parts.append(content)

    end = time.perf_counter()
    ttft = (first_token_at or end) - start
    duration = end - start
    words = max(1, len("".join(output_parts).split()))
    return {
        "ttft": ttft,
        "duration": duration,
        "words": words,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "chunks": chunks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000/v1")
    parser.add_argument("--model", default="qwen-coder")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    args = parser.parse_args()

    print(f"base_url={args.base_url}")
    print(f"model={args.model}")
    print(f"temperature={args.temperature}")
    print(f"top_p={args.top_p}")

    for index, prompt in enumerate(PROMPTS, start=1):
        try:
            result = stream_chat(
                args.base_url,
                args.model,
                prompt,
                args.max_tokens,
                args.temperature,
                args.top_p,
            )
        except urllib.error.URLError as exc:
            raise SystemExit(f"request failed: {exc}") from exc

        duration = float(result["duration"])
        completion_tokens = result["completion_tokens"]
        if completion_tokens:
            rate = completion_tokens / duration
            token_fields = (
                f"completion_tokens={completion_tokens} "
                f"prompt_tokens={result['prompt_tokens']} "
                f"tok_s={rate:.1f}"
            )
        else:
            words = int(result["words"])
            token_fields = f"words={words} word_rate={words / duration:.1f}/s"

        print(
            f"prompt={index} ttft={result['ttft']:.3f}s total={duration:.3f}s {token_fields}"
        )


if __name__ == "__main__":
    main()
