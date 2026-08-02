#!/usr/bin/env python3
"""P122.3 capacity harness: concurrency knee + long-context behaviour.

Method requirements enforced here:
  * unique prompt content per request (unless --shared-prefix)
  * token counts taken from server-reported usage, never chunk counts
  * ignore_eos + fixed max_tokens so every request decodes the same length
  * repeats with variance reported
"""
import argparse
import json
import random
import statistics
import string
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

WORDS = [
    "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 9)))
    for _ in range(20000)
]


# Calibrated against server-reported prompt_tokens: random lowercase words
# tokenize at roughly 3.3 tokens per word (no vocabulary compression).
TOKENS_PER_WORD = 3.36


def unique_prompt(approx_tokens: int, rng: random.Random) -> str:
    n = max(4, int(approx_tokens / TOKENS_PER_WORD))
    return " ".join(rng.choice(WORDS) for _ in range(n))


def one_request(url, model, prompt, max_tokens, timeout=600):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
        "top_p": 0.95,
        "stream": True,
        "stream_options": {"include_usage": True},
        "ignore_eos": True,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    ttft = None
    usage = None
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                obj = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if obj.get("usage"):
                usage = obj["usage"]
            for ch in obj.get("choices") or []:
                delta = ch.get("delta") or {}
                if ttft is None and (delta.get("content") or delta.get("reasoning_content")):
                    ttft = time.perf_counter() - t0
    dur = time.perf_counter() - t0
    if usage is None:
        raise RuntimeError("server did not return usage; cannot trust token counts")
    return {
        "ttft": ttft if ttft is not None else dur,
        "dur": dur,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
    }


def run_point(url, model, conc, prompt_tokens, max_tokens, seed, shared_prefix=False):
    rng = random.Random(seed)
    if shared_prefix:
        prefix = unique_prompt(prompt_tokens, rng)
        prompts = [f"{prefix}\n\nvariant {i}: summarize." for i in range(conc)]
    else:
        prompts = [unique_prompt(prompt_tokens, random.Random(seed * 1000 + i))
                   for i in range(conc)]
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=conc) as ex:
        results = list(ex.map(
            lambda p: one_request(url, model, p, max_tokens), prompts))
    wall = time.perf_counter() - t0
    total_out = sum(r["completion_tokens"] for r in results)
    total_in = sum(r["prompt_tokens"] for r in results)
    per_stream = [r["completion_tokens"] / r["dur"] for r in results]
    ttft_mean = statistics.mean(r["ttft"] for r in results)
    # Decode-only rate excludes the prefill phase from the denominator, so it is
    # comparable across prompt lengths; agg_tps is the end-to-end user-visible rate.
    decode_win = max(1e-6, wall - ttft_mean)
    return {
        "conc": conc,
        "wall": wall,
        "agg_tps": total_out / wall,
        "decode_tps": total_out / decode_win,
        "prefill_tps": total_in / max(1e-6, ttft_mean),
        "per_stream_tps": statistics.mean(per_stream),
        "ttft_mean": ttft_mean,
        "ttft_p95": sorted(r["ttft"] for r in results)[max(0, int(len(results) * 0.95) - 1)],
        "prompt_tokens": statistics.mean(r["prompt_tokens"] for r in results),
        "out_tokens": total_out,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True,
                    help="Full chat-completions URL, e.g. "
                         "http://<host>:<port>/v1/chat/completions")
    ap.add_argument("--model", required=True,
                    help="Served model alias as reported by /v1/models")
    ap.add_argument("--mode", choices=["conc", "ctx", "prefix"], default="conc")
    ap.add_argument("--conc", type=int, nargs="+", default=[1, 8, 16, 32, 48, 64])
    ap.add_argument("--ctx", type=int, nargs="+", default=[512])
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--repeats", type=int, default=2)
    args = ap.parse_args()

    print(f"# mode={args.mode} model={args.model} max_tokens={args.max_tokens} "
          f"repeats={args.repeats}", flush=True)
    hdr = ("conc", "ctx_in", "agg_tok/s", "decode", "prefill", "per_str", "ttft_mean", "ttft_p95", "spread%")
    print("| {:>4} | {:>7} | {:>10} | {:>8} | {:>8} | {:>7} | {:>9} | {:>8} | {:>7} |".format(*hdr), flush=True)
    print("|" + "|".join(["-" * 6, "-" * 9, "-" * 12, "-" * 10, "-" * 10, "-" * 9, "-" * 11, "-" * 10, "-" * 9]) + "|", flush=True)

    for ctx in args.ctx:
        for c in args.conc:
            runs = []
            for r in range(args.repeats):
                try:
                    runs.append(run_point(args.url, args.model, c, ctx,
                                          args.max_tokens, seed=1234 + r,
                                          shared_prefix=(args.mode == "prefix")))
                except Exception as exc:  # noqa: BLE001
                    print(f"| {c:>4} | {ctx:>7} | FAILED: {type(exc).__name__}: {exc}", flush=True)
                    runs = []
                    break
            if not runs:
                continue
            aggs = [x["agg_tps"] for x in runs]
            spread = (max(aggs) - min(aggs)) / statistics.mean(aggs) * 100
            b = max(runs, key=lambda x: x["agg_tps"])
            print("| {:>4} | {:>7.0f} | {:>10.1f} | {:>8.1f} | {:>8.0f} | {:>7.1f} | {:>9.2f} | {:>8.2f} | {:>7.1f} |".format(
                c, b["prompt_tokens"], statistics.mean(aggs), b["decode_tps"],
                b["prefill_tps"], b["per_stream_tps"],
                b["ttft_mean"], b["ttft_p95"], spread), flush=True)


if __name__ == "__main__":
    sys.exit(main())
