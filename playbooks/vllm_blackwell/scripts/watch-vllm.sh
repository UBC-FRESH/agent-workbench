#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

interval="${INTERVAL:-2}"
base_url="${BASE_URL:-http://127.0.0.1:${VLLM_PORT:-18000}}"
log_path="${LOG_PATH:-}"
pid_file="${PID_FILE:-logs/vllm-copilot.pid}"
once="${ONCE:-0}"
no_clear="${NO_CLEAR:-0}"
verbose="${VERBOSE:-0}"
health_check="${HEALTH_CHECK:-0}"
show_warnings="${SHOW_WARNINGS:-0}"
show_recent="${SHOW_RECENT:-1}"

if [[ -z "$log_path" && -f logs/vllm-active.logpath ]]; then
  log_path="$(cat logs/vllm-active.logpath)"
fi

if [[ -z "$log_path" ]]; then
  log_path="$(ls -1t logs/vllm-*.log 2>/dev/null | head -1 || true)"
fi

read_pid() {
  if [[ -f "$pid_file" ]]; then
    cat "$pid_file"
  fi
}

print_gpu() {
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "nvidia-smi not found"
    return
  fi

  nvidia-smi \
    --query-gpu=index,name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw \
    --format=csv,noheader,nounits \
    | python3 -c '
import sys
line = sys.stdin.read().strip()
if not line:
    print("gpu unavailable")
    raise SystemExit
parts = [part.strip() for part in line.split(",")]
if len(parts) < 8:
    print(line)
    raise SystemExit
idx, name, gpu_util, mem_util, mem_used, mem_total, temp, power = parts[:8]
print(f"gpu{idx}: {gpu_util}% core / {mem_util}% mem | {float(mem_used)/1024:.1f}/{float(mem_total)/1024:.1f} GiB | {temp}C | {float(power):.0f}W")
'
}

print_server() {
  local server_pid
  server_pid="$(read_pid || true)"

  if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    printf 'server: running pid=%s' "$server_pid"
  elif [[ -n "$server_pid" ]]; then
    printf 'server: stopped pid=%s' "$server_pid"
  else
    printf 'server: pid unknown'
  fi

  if [[ "$health_check" == "1" ]]; then
    local health_status
    health_status="$(curl -fsS --max-time 1 "$base_url/health" >/dev/null 2>&1 && echo ok || echo fail)"
    printf ' | health=%s' "$health_status"
  fi

  printf '\n'
  echo "url: $base_url | log: ${log_path:-unknown}"
}

print_metrics() {
  local metrics_file
  metrics_file="$(mktemp)"

  if ! curl -fsS --max-time 2 "$base_url/metrics" >"$metrics_file" 2>/dev/null; then
    echo "metrics unavailable"
    rm -f "$metrics_file"
    return
  fi

  python3 - "$metrics_file" "$verbose" <<'PY'
import math
import sys

metrics_path = sys.argv[1]
verbose = sys.argv[2] == "1"
wanted_names = {
    "vllm:spec_decode_num_draft_tokens_total",
    "vllm:spec_decode_num_accepted_tokens_total",
    "vllm:num_requests_running",
    "vllm:num_requests_waiting",
    "vllm:num_requests_waiting_by_reason",
    "vllm:gpu_cache_usage_perc",
    "vllm:prefix_cache_queries_total",
    "vllm:prefix_cache_hits_total",
    "vllm:prompt_tokens_total",
    "vllm:generation_tokens_total",
}
values: dict[str, float] = {}
waiting_by_reason: dict[str, float] = {}

with open(metrics_path, encoding="utf-8") as metrics:
    for line in metrics:
        if line.startswith("#") or not line.strip():
            continue
        try:
            metric, value = line.rsplit(maxsplit=1)
            name = metric.split("{", 1)[0]
        except ValueError:
            continue
        if name not in wanted_names:
            continue
        values.setdefault(name, float(value))
        if name == "vllm:num_requests_waiting_by_reason":
            reason = "unknown"
            if "reason=\"" in metric:
                reason = metric.split("reason=\"", 1)[1].split("\"", 1)[0]
            waiting_by_reason[reason] = float(value)
        if verbose:
            print(line.rstrip())

running = values.get("vllm:num_requests_running", 0.0)
waiting = values.get("vllm:num_requests_waiting", 0.0)
prompt_tokens = values.get("vllm:prompt_tokens_total", 0.0)
generation_tokens = values.get("vllm:generation_tokens_total", 0.0)
gpu_cache = values.get("vllm:gpu_cache_usage_perc")
if gpu_cache is not None:
    gpu_cache *= 100

waiting_detail = ""
if waiting_by_reason:
    nonzero_waiting = {
        reason: value for reason, value in waiting_by_reason.items() if value
    }
    if nonzero_waiting:
        waiting_detail = " (" + ", ".join(
            f"{reason}={value:.0f}" for reason, value in sorted(nonzero_waiting.items())
        ) + ")"

print(f"requests  running {running:.0f}  waiting {waiting:.0f}{waiting_detail}")
if gpu_cache is not None:
    print(f"kv cache  {gpu_cache:.1f}%")
print(f"tokens    prompt {prompt_tokens:,.0f}  generated {generation_tokens:,.0f}")

prefix_queries = values.get("vllm:prefix_cache_queries_total", 0.0)
prefix_hits = values.get("vllm:prefix_cache_hits_total", 0.0)
if prefix_queries > 0 and math.isfinite(prefix_queries):
    print(f"prefix    {(prefix_hits / prefix_queries) * 100:.1f}% hit")

draft_tokens = values.get("vllm:spec_decode_num_draft_tokens_total", 0.0)
accepted_tokens = values.get("vllm:spec_decode_num_accepted_tokens_total", 0.0)
if draft_tokens > 0 and math.isfinite(draft_tokens):
    print(f"spec      {(accepted_tokens / draft_tokens) * 100:.1f}% accepted")
PY

  rm -f "$metrics_file"
}

print_throughput() {
  if [[ -z "$log_path" || ! -f "$log_path" ]]; then
    echo "throughput unavailable"
    return
  fi

  local latest
  latest="$(grep 'Avg prompt throughput:' "$log_path" | tail -1 || true)"
  if [[ -z "$latest" ]]; then
    echo "throughput unavailable"
    return
  fi

  python3 - "$latest" <<'PY'
import re
import sys

line = sys.argv[1]
patterns = {
    "prompt_tok_s": r"Avg prompt throughput: ([0-9.]+) tokens/s",
    "gen_tok_s": r"Avg generation throughput: ([0-9.]+) tokens/s",
    "running": r"Running: ([0-9]+) reqs",
    "waiting": r"Waiting: ([0-9]+) reqs",
    "kv": r"GPU KV cache usage: ([0-9.]+)%",
    "prefix": r"Prefix cache hit rate: ([0-9.]+)%",
}
values = {}
for key, pattern in patterns.items():
    match = re.search(pattern, line)
    if match:
        values[key] = match.group(1)

if values:
    print(
        "throughput "
        f"prompt {values.get('prompt_tok_s', '?')} tok/s  "
        f"gen {values.get('gen_tok_s', '?')} tok/s  "
        f"run {values.get('running', '?')}  wait {values.get('waiting', '?')}  "
        f"kv {values.get('kv', '?')}%  prefix {values.get('prefix', '?')}%"
    )
else:
    print("throughput parse failed")
PY
}

print_log_summary() {
  if [[ -z "$log_path" || ! -f "$log_path" ]]; then
    echo "log unavailable"
    return
  fi

  if [[ "$verbose" == "1" ]]; then
    tail -300 "$log_path" \
      | grep -E 'POST /v1/chat/completions|GET /v1/models|Avg prompt throughput|SpecDecoding metrics|GPU KV cache size|Maximum concurrency|ERROR|WARNING|Traceback' \
      | tail -35 \
      || true
    return
  fi

  if [[ "$show_recent" != "1" && "$show_warnings" != "1" ]]; then
    return
  fi

  local requests
  local warnings
  requests="$(grep 'POST /v1/chat/completions' "$log_path" | tail -5 | sed -E 's/^.*INFO: +//; s/ - "/ "/' || true)"
  warnings="$(grep -E 'ERROR|Traceback|CUDA out of memory|OOM|HTTP/1.1\" [45][0-9][0-9]' "$log_path" | tail -3 || true)"

  if [[ "$show_recent" == "1" ]]; then
    if [[ -n "$requests" ]]; then
      echo "$requests"
    else
      echo "no recent chat completions"
    fi
  fi

  if [[ "$show_warnings" == "1" && -n "$warnings" ]]; then
    echo
    echo "alerts:"
    echo "$warnings" | sed 's/^/  /'
  fi
}

render() {
  if [[ "$no_clear" != "1" ]]; then
    clear || true
  fi

  echo "== vLLM Watch :: $(date '+%Y-%m-%d %H:%M:%S %Z') =="
  echo
  echo "-- Server --"
  print_server
  echo
  echo "GPU"
  print_gpu
  echo
  echo "Load"
  print_throughput
  print_metrics
  if [[ "$show_recent" == "1" || "$show_warnings" == "1" || "$verbose" == "1" ]]; then
    echo
    echo "Recent"
    print_log_summary
  fi
}

while true; do
  render
  if [[ "$once" == "1" ]]; then
    break
  fi
  sleep "$interval"
done
