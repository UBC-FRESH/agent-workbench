"""Resumable OpenAI-compatible document metadata extraction."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import statistics
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_SYSTEM_PROMPT = """You extract auditable metadata from a document chunk.
Return only a JSON object with a `records` array. Every record must use this schema:
{
  "record_type": "string",
  "title_or_heading": "string or null",
  "summary": "string",
  "entities": ["string"],
  "dates": ["string"],
  "locations": ["string"],
  "methods_or_actions": ["string"],
  "constraints_or_thresholds": ["string"],
  "evidence_quotes": ["short exact quote"],
  "confidence": 0.0,
  "warnings": ["string"]
}
Use an empty records array only when the source contains no relevant metadata.
Do not invent facts. Evidence quotes must be copied from the supplied text."""

REQUIRED_RECORD_FIELDS = {
    "record_type": str,
    "title_or_heading": (str, type(None)),
    "summary": str,
    "entities": list,
    "dates": list,
    "locations": list,
    "methods_or_actions": list,
    "constraints_or_thresholds": list,
    "evidence_quotes": list,
    "confidence": (int, float),
    "warnings": list,
}


@dataclass(frozen=True)
class EndpointProfile:
    name: str
    base_url: str
    model: str
    api_key: str | None
    timeout_seconds: float
    max_tokens: int
    temperature: float
    json_mode: bool


@dataclass(frozen=True)
class ChunkJob:
    chunk_id: str
    document_id: str
    source_pages: list[int]
    text_path: Path


@dataclass(frozen=True)
class RunConfig:
    cpu_profile: EndpointProfile
    gpu_profile: EndpointProfile | None
    output_path: Path
    summary_path: Path
    workers: int
    retry_failed: bool
    max_cpu_attempts: int


def now_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{line_number}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            raise ValueError(f"{path}:{line_number}: empty key")
        values[key] = value
    return values


def profile_from_env(name: str, path: Path) -> EndpointProfile:
    values = read_env_file(path)
    required = ("AW_SCRAPER_BASE_URL", "AW_SCRAPER_MODEL")
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise ValueError(
            f"{path}: missing required profile values: {', '.join(missing)}"
        )
    return EndpointProfile(
        name=name,
        base_url=values["AW_SCRAPER_BASE_URL"].rstrip("/"),
        model=values["AW_SCRAPER_MODEL"],
        api_key=values.get("AW_SCRAPER_API_KEY") or None,
        timeout_seconds=float(values.get("AW_SCRAPER_TIMEOUT_SECONDS", "90")),
        max_tokens=int(values.get("AW_SCRAPER_MAX_TOKENS", "1200")),
        temperature=float(values.get("AW_SCRAPER_TEMPERATURE", "0")),
        json_mode=values.get("AW_SCRAPER_JSON_MODE", "true").lower()
        in {"1", "true", "yes"},
    )


def load_chunk_jobs(manifest_path: Path, project_root: Path) -> list[ChunkJob]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(manifest.get("documents"), list):
        jobs: list[ChunkJob] = []
        for document in manifest["documents"]:
            nested_path = document.get("manifest_path")
            if not isinstance(nested_path, str):
                raise ValueError("global manifest document missing manifest_path")
            jobs.extend(load_chunk_jobs(project_root / nested_path, project_root))
        return jobs

    document_id = manifest.get("document_id")
    chunks = manifest.get("chunks")
    if not isinstance(document_id, str) or not isinstance(chunks, list):
        raise ValueError(f"{manifest_path}: expected document_id and chunks")
    jobs = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            raise ValueError(f"{manifest_path}: chunk must be an object")
        chunk_id = chunk.get("chunk_id")
        text_value = chunk.get("runtime_text_path", chunk.get("raw_text_path"))
        page_start = chunk.get("page_start")
        page_end = chunk.get("page_end")
        if not isinstance(chunk_id, str) or not isinstance(text_value, str):
            raise ValueError(f"{manifest_path}: chunk requires chunk_id and text path")
        if not isinstance(page_start, int) or not isinstance(page_end, int):
            raise ValueError(f"{manifest_path}: chunk {chunk_id} requires page bounds")
        text_path = Path(text_value)
        if not text_path.is_absolute():
            text_path = project_root / text_path
        jobs.append(
            ChunkJob(
                chunk_id=chunk_id,
                document_id=document_id,
                source_pages=list(range(page_start, page_end + 1)),
                text_path=text_path,
            )
        )
    return jobs


def completed_chunk_ids(output_path: Path, retry_failed: bool) -> set[str]:
    if not output_path.exists():
        return set()
    completed: set[str] = set()
    for line_number, line in enumerate(
        output_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{output_path}:{line_number}: invalid JSONL checkpoint"
            ) from error
        chunk_id = entry.get("chunk_id")
        status = entry.get("status")
        if not isinstance(chunk_id, str) or not isinstance(status, str):
            raise ValueError(f"{output_path}:{line_number}: missing chunk_id or status")
        if status == "completed" or (status == "failed" and not retry_failed):
            completed.add(chunk_id)
    return completed


def request_records(
    profile: EndpointProfile, job: ChunkJob, text: str
) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {
        "model": profile.model,
        "temperature": profile.temperature,
        "max_tokens": profile.max_tokens,
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Chunk ID: {job.chunk_id}\nDocument ID: {job.document_id}\n"
                    f"Source pages: {job.source_pages}\n\nDocument text:\n{text}"
                ),
            },
        ],
    }
    if profile.json_mode:
        payload["response_format"] = {"type": "json_object"}
    encoded = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if profile.api_key:
        headers["Authorization"] = f"Bearer {profile.api_key}"
    request = Request(
        f"{profile.base_url}/chat/completions",
        data=encoded,
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=profile.timeout_seconds) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"http_{error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"network_error: {error.reason}") from error
    except TimeoutError as error:
        raise RuntimeError("request_timeout") from error
    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("invalid_openai_response") from error
    if not isinstance(content, str):
        raise RuntimeError("non_text_model_response")
    return validate_records(parse_json_object(content), job)


def parse_json_object(content: str) -> dict[str, Any]:
    candidate = content.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", candidate, re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"invalid_model_json: {error.msg}") from error
    if not isinstance(parsed, dict):
        raise RuntimeError("model_json_must_be_an_object")
    return parsed


def validate_records(payload: dict[str, Any], job: ChunkJob) -> list[dict[str, Any]]:
    records = payload.get("records")
    if not isinstance(records, list):
        raise RuntimeError("model_json_missing_records_array")
    validated: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise RuntimeError(f"record_{index}_must_be_an_object")
        missing = [name for name in REQUIRED_RECORD_FIELDS if name not in record]
        if missing:
            raise RuntimeError(f"record_{index}_missing_fields: {', '.join(missing)}")
        for field_name, expected_type in REQUIRED_RECORD_FIELDS.items():
            if not isinstance(record[field_name], expected_type):
                raise RuntimeError(f"record_{index}_{field_name}_has_invalid_type")
        if not 0 <= float(record["confidence"]) <= 1:
            raise RuntimeError(f"record_{index}_confidence_out_of_range")
        for field_name in (
            "entities",
            "dates",
            "locations",
            "methods_or_actions",
            "constraints_or_thresholds",
            "evidence_quotes",
            "warnings",
        ):
            if not all(isinstance(value, str) for value in record[field_name]):
                raise RuntimeError(f"record_{index}_{field_name}_must_contain_strings")
        normalized = dict(record)
        normalized["chunk_id"] = job.chunk_id
        normalized["document_id"] = job.document_id
        normalized["source_pages"] = job.source_pages
        validated.append(normalized)
    return validated


def process_job(job: ChunkJob, config: RunConfig) -> dict[str, Any]:
    started = time.monotonic()
    attempts: list[dict[str, Any]] = []
    try:
        text = job.text_path.read_text(encoding="utf-8")
    except OSError as error:
        return failure_entry(job, started, attempts, "input_error", str(error))
    for attempt_number in range(1, config.max_cpu_attempts + 1):
        try:
            records = request_records(config.cpu_profile, job, text)
            attempts.append(
                {
                    "lane": "cpu",
                    "profile": config.cpu_profile.name,
                    "status": "completed",
                }
            )
            return success_entry(job, started, attempts, records, "cpu")
        except RuntimeError as error:
            attempts.append(
                {
                    "lane": "cpu",
                    "profile": config.cpu_profile.name,
                    "attempt": attempt_number,
                    "status": "failed",
                    "error": str(error),
                }
            )
    if config.gpu_profile is not None:
        try:
            records = request_records(config.gpu_profile, job, text)
            attempts.append(
                {
                    "lane": "gpu",
                    "profile": config.gpu_profile.name,
                    "status": "completed",
                }
            )
            return success_entry(job, started, attempts, records, "gpu_fallback")
        except RuntimeError as error:
            attempts.append(
                {
                    "lane": "gpu",
                    "profile": config.gpu_profile.name,
                    "attempt": 1,
                    "status": "failed",
                    "error": str(error),
                }
            )
    error_message = attempts[-1]["error"] if attempts else "no_attempts"
    return failure_entry(job, started, attempts, "extraction_error", error_message)


def success_entry(
    job: ChunkJob,
    started: float,
    attempts: list[dict[str, Any]],
    records: list[dict[str, Any]],
    route: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "completed_utc": now_utc(),
        "chunk_id": job.chunk_id,
        "document_id": job.document_id,
        "source_pages": job.source_pages,
        "status": "completed",
        "route": route,
        "duration_seconds": round(time.monotonic() - started, 3),
        "attempts": attempts,
        "records": records,
    }


def failure_entry(
    job: ChunkJob,
    started: float,
    attempts: list[dict[str, Any]],
    category: str,
    error: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "completed_utc": now_utc(),
        "chunk_id": job.chunk_id,
        "document_id": job.document_id,
        "source_pages": job.source_pages,
        "status": "failed",
        "route": "failed",
        "duration_seconds": round(time.monotonic() - started, 3),
        "attempts": attempts,
        "error": {"category": category, "message": error},
        "records": [],
    }


def resource_observations() -> dict[str, Any]:
    observations: dict[str, Any] = {"host_cpu_count": os.cpu_count()}
    try:
        observations["load_average"] = list(os.getloadavg())
    except OSError:
        pass
    status_path = Path("/proc/self/status")
    if status_path.exists():
        for line in status_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                observations["coordinator_rss_kb"] = int(line.split()[1])
                break
    return observations


def write_summary(
    entries: list[dict[str, Any]],
    config: RunConfig,
    run_id: str,
    total_jobs: int,
    processed_this_run: int,
) -> dict[str, Any]:
    durations = [entry["duration_seconds"] for entry in entries]
    completed = [entry for entry in entries if entry["status"] == "completed"]
    cpu_completed = [entry for entry in completed if entry["route"] == "cpu"]
    gpu_completed = [entry for entry in completed if entry["route"] == "gpu_fallback"]
    failures = [entry for entry in entries if entry["status"] == "failed"]
    retries = sum(
        max(
            0,
            len([attempt for attempt in entry["attempts"] if attempt["lane"] == "cpu"])
            - 1,
        )
        for entry in entries
    )
    total_duration = sum(durations)
    summary = {
        "schema_version": 1,
        "phase": "P120",
        "run_id": run_id,
        "generated_utc": now_utc(),
        "inputs": {
            "selected_jobs": total_jobs,
            "processed_jobs": len(entries),
            "processed_this_run": processed_this_run,
            "cpu_profile": public_profile(config.cpu_profile),
            "gpu_profile": public_profile(config.gpu_profile)
            if config.gpu_profile
            else None,
        },
        "quality": {
            "completed_chunks": len(completed),
            "failed_chunks": len(failures),
            "valid_record_rate": safe_rate(len(completed), len(entries)),
            "cpu_first_pass_or_retry_success_rate": safe_rate(
                len(cpu_completed), len(entries)
            ),
            "gpu_fallback_successes": len(gpu_completed),
            "explicit_failure_records": len(failures),
        },
        "protocol": {
            "checkpoint_path": str(config.output_path),
            "append_safe_jsonl": True,
            "retry_failed_requested": config.retry_failed,
            "max_cpu_attempts": config.max_cpu_attempts,
            "fallback_enabled": config.gpu_profile is not None,
            "unprocessed_jobs": total_jobs - len(entries),
        },
        "economics": {
            "processed_chunks_per_hour": safe_rate(len(entries) * 3600, total_duration),
            "validated_chunks_per_hour": safe_rate(
                len(completed) * 3600, total_duration
            ),
            "documents_with_completed_chunks": len(
                {entry["document_id"] for entry in completed}
            ),
            "documents_per_hour": safe_rate(
                len({entry["document_id"] for entry in completed}) * 3600,
                total_duration,
            ),
            "mean_chunk_latency_seconds": statistics.mean(durations)
            if durations
            else None,
            "p95_chunk_latency_seconds": percentile(durations, 0.95),
            "cpu_retry_count": retries,
            "gpu_fallback_rate": safe_rate(len(gpu_completed), len(entries)),
            "resource_observations": resource_observations(),
            "provider_cost": "not captured by this coordinator",
        },
    }
    config.summary_path.parent.mkdir(parents=True, exist_ok=True)
    config.summary_path.write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def public_profile(profile: EndpointProfile) -> dict[str, Any]:
    return {
        "name": profile.name,
        "model": profile.model,
        "timeout_seconds": profile.timeout_seconds,
        "max_tokens": profile.max_tokens,
        "temperature": profile.temperature,
        "json_mode": profile.json_mode,
    }


def safe_rate(numerator: float, denominator: float) -> float | None:
    if not denominator:
        return None
    return round(numerator / denominator, 6)


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * fraction)))
    return ordered[index]


def run(config: RunConfig, jobs: list[ChunkJob]) -> dict[str, Any]:
    pending_ids = completed_chunk_ids(config.output_path, config.retry_failed)
    pending_jobs = [job for job in jobs if job.chunk_id not in pending_ids]
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    write_lock = threading.Lock()
    entries: list[dict[str, Any]] = []
    with config.output_path.open("a", encoding="utf-8") as checkpoint:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=config.workers
        ) as executor:
            futures = [
                executor.submit(process_job, job, config) for job in pending_jobs
            ]
            for future in concurrent.futures.as_completed(futures):
                entry = future.result()
                with write_lock:
                    checkpoint.write(json.dumps(entry, sort_keys=True) + "\n")
                    checkpoint.flush()
                    os.fsync(checkpoint.fileno())
                entries.append(entry)
    all_entries = checkpoint_entries(config.output_path)
    return write_summary(
        all_entries,
        config,
        uuid.uuid4().hex,
        len(jobs),
        len(entries),
    )


def checkpoint_entries(output_path: Path) -> list[dict[str, Any]]:
    latest_entries: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(
        output_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{output_path}:{line_number}: invalid JSONL checkpoint"
            ) from error
        chunk_id = entry.get("chunk_id")
        if not isinstance(chunk_id, str):
            raise ValueError(f"{output_path}:{line_number}: missing chunk_id")
        latest_entries[chunk_id] = entry
    return list(latest_entries.values())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cpu-profile", type=Path, required=True)
    parser.add_argument("--gpu-profile", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--chunk-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--max-cpu-attempts", type=int, default=2)
    arguments = parser.parse_args(argv)
    if arguments.workers < 1:
        parser.error("--workers must be at least 1")
    if arguments.limit is not None and arguments.limit < 1:
        parser.error("--limit must be at least 1")
    if arguments.max_cpu_attempts < 1:
        parser.error("--max-cpu-attempts must be at least 1")
    return arguments


def main(argv: list[str] | None = None) -> int:
    arguments = parse_args(argv)
    project_root = arguments.project_root.resolve()
    manifest_path = arguments.manifest
    if not manifest_path.is_absolute():
        manifest_path = project_root / manifest_path
    jobs = load_chunk_jobs(manifest_path, project_root)
    if arguments.chunk_id:
        requested = set(arguments.chunk_id)
        jobs = [job for job in jobs if job.chunk_id in requested]
        missing = requested - {job.chunk_id for job in jobs}
        if missing:
            raise SystemExit(f"unknown chunk IDs: {', '.join(sorted(missing))}")
    if arguments.limit is not None:
        jobs = jobs[: arguments.limit]
    output_path = (
        arguments.output
        if arguments.output.is_absolute()
        else project_root / arguments.output
    )
    summary_path = (
        arguments.summary
        if arguments.summary.is_absolute()
        else project_root / arguments.summary
    )
    cpu_profile_path = arguments.cpu_profile
    if not cpu_profile_path.is_absolute():
        cpu_profile_path = project_root / cpu_profile_path
    gpu_profile_path = arguments.gpu_profile
    if gpu_profile_path is not None and not gpu_profile_path.is_absolute():
        gpu_profile_path = project_root / gpu_profile_path
    config = RunConfig(
        cpu_profile=profile_from_env("cpu", cpu_profile_path),
        gpu_profile=profile_from_env("gpu_fallback", gpu_profile_path)
        if gpu_profile_path
        else None,
        output_path=output_path,
        summary_path=summary_path,
        workers=arguments.workers,
        retry_failed=arguments.retry_failed,
        max_cpu_attempts=arguments.max_cpu_attempts,
    )
    summary = run(config, jobs)
    print(json.dumps(summary, indent=2))
    return 0 if summary["quality"]["failed_chunks"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
