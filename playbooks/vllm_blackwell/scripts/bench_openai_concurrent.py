#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import statistics
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


BASE_TASKS = [
    "Summarize the recurring design constraints in the context, then propose a careful implementation plan.",
    "Find the most important tradeoffs in the context and rank them by operational risk.",
    "Extract the assumptions from the context, identify weak assumptions, and suggest validation steps.",
    "Write a concise engineering decision record based on the context.",
    "Design a debugging checklist for the system described in the context.",
    "Explain what should be optimized first and what should be left alone.",
    "Propose a rollout strategy that preserves rollback safety.",
    "List the likely failure modes and the signals that would reveal them.",
]

CONTEXT_PARAGRAPH = (
    "In a local inference deployment, KV cache capacity determines how many long-context "
    "requests can remain resident on the GPU at the same time. Decode throughput matters "
    "for single-user latency, but prefill cost, cache pressure, scheduler behavior, and "
    "preemption determine whether concurrent agents complete smoothly under load. "
)


@dataclass(frozen=True)
class Result:
    index: int
    ok: bool
    ttft: float
    duration: float
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    chunks: int
    error: str | None = None


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((pct / 100) * (len(ordered) - 1))))
    return ordered[index]


def make_context(target_words: int) -> str:
    words: list[str] = []
    paragraph_words = CONTEXT_PARAGRAPH.split()
    while len(words) < target_words:
        words.extend(paragraph_words)
    return " ".join(words[:target_words])


def stream_chat(
    base_url: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    timeout: float,
) -> tuple[float, float, int | None, int | None, int | None, int]:
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
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    with urllib.request.urlopen(request, timeout=timeout) as response:
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
            content = choices[0].get("delta", {}).get("content")
            if content:
                if first_token_at is None:
                    first_token_at = time.perf_counter()
                chunks += 1

    end = time.perf_counter()
    return (
        (first_token_at or end) - start,
        end - start,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        chunks,
    )


def run_one(
    index: int,
    base_url: str,
    model: str,
    context: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    timeout: float,
) -> Result:
    task = BASE_TASKS[index % len(BASE_TASKS)]
    prompt = f"{context}\n\nRequest {index + 1}: {task}"
    try:
        ttft, duration, prompt_tokens, completion_tokens, total_tokens, chunks = (
            stream_chat(
                base_url, model, prompt, max_tokens, temperature, top_p, timeout
            )
        )
        return Result(
            index,
            True,
            ttft,
            duration,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            chunks,
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return Result(index, False, 0.0, 0.0, None, None, None, 0, str(exc))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000/v1")
    parser.add_argument("--model", default="qwen-coder")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--requests", type=int, default=4)
    parser.add_argument("--context-words", type=int, default=2000)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--timeout", type=float, default=900)
    args = parser.parse_args()

    context = make_context(args.context_words)
    print(f"base_url={args.base_url}")
    print(f"model={args.model}")
    print(f"requests={args.requests}")
    print(f"concurrency={args.concurrency}")
    print(f"context_words={args.context_words}")
    print(f"max_tokens={args.max_tokens}")
    print(f"temperature={args.temperature}")
    print(f"top_p={args.top_p}")

    start = time.perf_counter()
    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.concurrency
    ) as executor:
        futures = [
            executor.submit(
                run_one,
                index,
                args.base_url,
                args.model,
                context,
                args.max_tokens,
                args.temperature,
                args.top_p,
                args.timeout,
            )
            for index in range(args.requests)
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            if result.ok:
                completion = result.completion_tokens or 0
                prompt = result.prompt_tokens or 0
                print(
                    f"request={result.index + 1} ok=1 ttft={result.ttft:.3f}s "
                    f"total={result.duration:.3f}s prompt_tokens={prompt} "
                    f"completion_tokens={completion} tok_s={completion / result.duration if result.duration else 0:.1f}"
                )
            else:
                print(f"request={result.index + 1} ok=0 error={result.error}")

    wall = time.perf_counter() - start
    successes = [result for result in results if result.ok]
    failures = [result for result in results if not result.ok]
    durations = [result.duration for result in successes]
    ttfts = [result.ttft for result in successes]
    completion_tokens = sum(result.completion_tokens or 0 for result in successes)
    prompt_tokens = sum(result.prompt_tokens or 0 for result in successes)

    print("summary")
    print(f"ok={len(successes)} failed={len(failures)} wall={wall:.3f}s")
    print(f"prompt_tokens={prompt_tokens} completion_tokens={completion_tokens}")
    print(f"aggregate_completion_tok_s={completion_tokens / wall if wall else 0:.1f}")
    if durations:
        print(
            "latency "
            f"mean={statistics.mean(durations):.3f}s "
            f"p50={statistics.median(durations):.3f}s "
            f"p95={percentile(durations, 95):.3f}s"
        )
        print(
            "ttft "
            f"mean={statistics.mean(ttfts):.3f}s "
            f"p50={statistics.median(ttfts):.3f}s "
            f"p95={percentile(ttfts, 95):.3f}s"
        )


if __name__ == "__main__":
    main()
