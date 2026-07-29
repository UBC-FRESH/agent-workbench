"""Coordinate short-lived Slurm GPU allocations across SSH-accessible clusters.

The coordinator is deliberately conservative:

* normal invocations are observe/dry-run only;
* ``--apply`` is required before it submits or cancels anything;
* it persists only job IDs it submitted itself; and
* it only cancels those tracked jobs while they are still pending.

This keeps a capacity search from interfering with independent user workloads
or with allocations created outside this tool.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import yaml


class CapacityCoordinatorError(RuntimeError):
    """Raised when configuration or a remote Slurm operation is invalid."""


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]

GPU_COUNT_PATTERN = re.compile(r"(?:gres/)?gpu(?::[^\s|,]+)*:(\d+)", re.IGNORECASE)
RUNNING_STATES = {"RUNNING", "R", "COMPLETING", "CG"}
PENDING_STATES = {"PENDING", "PD", "CONFIGURING", "CF"}


@dataclass(frozen=True)
class ClusterSpec:
    """One Slurm cluster that may receive allocation requests."""

    name: str
    ssh_target: str
    submission_script: str
    gpus_per_job: int
    partition: str | None = None
    account: str | None = None
    nodes: int = 1
    cpus_per_task: int = 4
    memory: str = "32G"
    time_limit: str = "12:00:00"
    constraint: str | None = None
    max_pending_jobs: int = 1
    sbatch_args: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ClusterSpec":
        required = ("name", "ssh_target", "submission_script", "gpus_per_job")
        missing = [key for key in required if not value.get(key)]
        if missing:
            raise CapacityCoordinatorError(
                f"cluster entry is missing required fields: {', '.join(missing)}"
            )
        gpus_per_job = int(value["gpus_per_job"])
        max_pending_jobs = int(value.get("max_pending_jobs", 1))
        if gpus_per_job < 1:
            raise CapacityCoordinatorError("gpus_per_job must be at least one")
        if max_pending_jobs < 1:
            raise CapacityCoordinatorError("max_pending_jobs must be at least one")
        return cls(
            name=str(value["name"]),
            ssh_target=str(value["ssh_target"]),
            submission_script=str(value["submission_script"]),
            gpus_per_job=gpus_per_job,
            partition=_optional_string(value.get("partition")),
            account=_optional_string(value.get("account")),
            nodes=int(value.get("nodes", 1)),
            cpus_per_task=int(value.get("cpus_per_task", 4)),
            memory=str(value.get("memory", "32G")),
            time_limit=str(value.get("time_limit", "12:00:00")),
            constraint=_optional_string(value.get("constraint")),
            max_pending_jobs=max_pending_jobs,
            sbatch_args=tuple(str(arg) for arg in value.get("sbatch_args", [])),
        )


@dataclass
class TrackedJob:
    """A submission created by this coordinator and safe for it to cancel."""

    cluster: str
    job_id: str
    gpus: int
    submitted_at: str
    state: str = "PENDING"
    reason: str = ""

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TrackedJob":
        return cls(
            cluster=str(value["cluster"]),
            job_id=str(value["job_id"]),
            gpus=int(value["gpus"]),
            submitted_at=str(value["submitted_at"]),
            state=str(value.get("state", "UNKNOWN")),
            reason=str(value.get("reason", "")),
        )


@dataclass(frozen=True)
class ClusterAvailability:
    """A conservative scheduler-visible inventory snapshot."""

    cluster: str
    total_gpus: int = 0
    idle_gpus: int = 0
    running_gpu_jobs: int = 0
    pending_gpu_jobs: int = 0
    error: str | None = None


@dataclass(frozen=True)
class CoordinatorAction:
    """One proposed or applied remote scheduler action."""

    kind: str
    cluster: str
    detail: str
    job_id: str | None = None
    applied: bool = False


@dataclass
class ReconcileReport:
    """Result of one monitor/submit/cancel reconciliation pass."""

    target_gpus: int
    active_gpus: int
    pending_gpus: int
    availability: list[ClusterAvailability] = field(default_factory=list)
    actions: list[CoordinatorAction] = field(default_factory=list)
    jobs: list[TrackedJob] = field(default_factory=list)

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "target_gpus": self.target_gpus,
            "active_gpus": self.active_gpus,
            "pending_gpus": self.pending_gpus,
            "availability": [asdict(item) for item in self.availability],
            "actions": [asdict(item) for item in self.actions],
            "jobs": [asdict(item) for item in self.jobs],
        }


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _default_runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), capture_output=True, text=True, check=False)


def _gpu_count(gres: str) -> int:
    return sum(int(match) for match in GPU_COUNT_PATTERN.findall(gres))


def _is_running(state: str) -> bool:
    return state.upper() in RUNNING_STATES


def _is_pending(state: str) -> bool:
    return state.upper() in PENDING_STATES


def load_clusters(config_path: Path) -> list[ClusterSpec]:
    """Load public-safe cluster request specifications from YAML."""
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise CapacityCoordinatorError(f"could not read config {config_path}: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise CapacityCoordinatorError("config must be a YAML mapping")
    clusters = raw.get("clusters")
    if not isinstance(clusters, list) or not clusters:
        raise CapacityCoordinatorError("config must contain a non-empty clusters list")
    specs = [ClusterSpec.from_mapping(item) for item in clusters if isinstance(item, Mapping)]
    if len(specs) != len(clusters):
        raise CapacityCoordinatorError("every cluster entry must be a YAML mapping")
    names = [spec.name for spec in specs]
    if len(set(names)) != len(names):
        raise CapacityCoordinatorError("cluster names must be unique")
    return specs


def load_state(state_path: Path) -> list[TrackedJob]:
    """Load coordinator-owned jobs; a missing state file represents no jobs."""
    if not state_path.exists():
        return []
    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CapacityCoordinatorError(f"could not load state {state_path}: {exc}") from exc
    if not isinstance(raw, Mapping) or not isinstance(raw.get("jobs", []), list):
        raise CapacityCoordinatorError("state must contain a jobs list")
    return [TrackedJob.from_mapping(item) for item in raw["jobs"] if isinstance(item, Mapping)]


def save_state(state_path: Path, jobs: Iterable[TrackedJob]) -> None:
    """Persist coordinator-owned jobs atomically."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "updated_at": _utc_now(), "jobs": [asdict(job) for job in jobs]}
    temporary = state_path.with_suffix(f"{state_path.suffix}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(state_path)


class SlurmOverSsh:
    """Minimal Slurm adapter that issues one quoted command per SSH invocation."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or _default_runner

    def _remote(self, cluster: ClusterSpec, args: Sequence[str]) -> str:
        completed = self._runner(["ssh", cluster.ssh_target, shlex.join(args)])
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()
            raise CapacityCoordinatorError(f"{cluster.name}: {' '.join(args[:2])} failed: {detail}")
        return completed.stdout

    def scan(self, cluster: ClusterSpec) -> ClusterAvailability:
        try:
            inventory = self._remote(cluster, ["sinfo", "-N", "-h", "-o", "%N|%t|%G"])
            queue = self._remote(
                cluster,
                ["squeue", "-h", "-t", "R,PD", "-o", "%i|%T|%b|%R"],
            )
        except CapacityCoordinatorError as exc:
            return ClusterAvailability(cluster=cluster.name, error=str(exc))
        total_gpus = 0
        idle_gpus = 0
        for line in inventory.splitlines():
            fields = [field.strip() for field in line.split("|")]
            if len(fields) < 3:
                continue
            count = _gpu_count(fields[2])
            total_gpus += count
            if fields[1].lower().startswith("idle"):
                idle_gpus += count
        running = 0
        pending = 0
        for line in queue.splitlines():
            fields = [field.strip() for field in line.split("|")]
            if len(fields) < 3:
                continue
            count = _gpu_count(fields[2])
            if not count:
                continue
            if _is_running(fields[1]):
                running += 1
            elif _is_pending(fields[1]):
                pending += 1
        return ClusterAvailability(
            cluster=cluster.name,
            total_gpus=total_gpus,
            idle_gpus=idle_gpus,
            running_gpu_jobs=running,
            pending_gpu_jobs=pending,
        )

    def job_states(self, cluster: ClusterSpec, job_ids: Sequence[str]) -> dict[str, tuple[str, str]]:
        if not job_ids:
            return {}
        output = self._remote(
            cluster,
            ["squeue", "-h", "-j", ",".join(job_ids), "-o", "%i|%T|%R"],
        )
        states: dict[str, tuple[str, str]] = {}
        for line in output.splitlines():
            fields = [field.strip() for field in line.split("|", 2)]
            if len(fields) >= 2:
                states[fields[0]] = (fields[1], fields[2] if len(fields) > 2 else "")
        return states

    def submit(self, cluster: ClusterSpec) -> str:
        args = [
            "sbatch",
            "--parsable",
            f"--nodes={cluster.nodes}",
            "--ntasks=1",
            f"--cpus-per-task={cluster.cpus_per_task}",
            f"--mem={cluster.memory}",
            f"--gpus={cluster.gpus_per_job}",
            f"--time={cluster.time_limit}",
        ]
        if cluster.partition:
            args.append(f"--partition={cluster.partition}")
        if cluster.account:
            args.append(f"--account={cluster.account}")
        if cluster.constraint:
            args.append(f"--constraint={cluster.constraint}")
        args.extend(cluster.sbatch_args)
        args.append(cluster.submission_script)
        output = self._remote(cluster, args).strip()
        job_id = output.split(";", 1)[0].strip()
        if not job_id or not re.fullmatch(r"\d+(?:_[\w\-]+)?", job_id):
            raise CapacityCoordinatorError(f"{cluster.name}: unrecognized sbatch output: {output!r}")
        return job_id

    def cancel(self, cluster: ClusterSpec, job_id: str) -> None:
        self._remote(cluster, ["scancel", job_id])


def _monitor_jobs(
    clusters: Mapping[str, ClusterSpec], jobs: list[TrackedJob], adapter: SlurmOverSsh
) -> None:
    for cluster_name, spec in clusters.items():
        cluster_jobs = [job for job in jobs if job.cluster == cluster_name]
        try:
            states = adapter.job_states(spec, [job.job_id for job in cluster_jobs])
        except CapacityCoordinatorError as exc:
            for job in cluster_jobs:
                job.state = "UNKNOWN"
                job.reason = str(exc)
            continue
        for job in cluster_jobs:
            state = states.get(job.job_id)
            if state is None:
                if _is_running(job.state) or _is_pending(job.state):
                    job.state = "UNKNOWN"
                    job.reason = "not returned by squeue"
                continue
            job.state, job.reason = state


def reconcile_capacity(
    clusters: Sequence[ClusterSpec],
    jobs: list[TrackedJob],
    target_gpus: int,
    *,
    apply: bool = False,
    adapter: SlurmOverSsh | None = None,
) -> ReconcileReport:
    """Monitor tracked jobs and make a conservative capacity plan.

    When ``apply`` is false the report lists would-be submissions/cancellations
    but does not call ``sbatch`` or ``scancel``.  ``apply`` only ever cancels
    tracked jobs that are still pending.
    """
    if target_gpus < 1:
        raise CapacityCoordinatorError("target_gpus must be at least one")
    adapter = adapter or SlurmOverSsh()
    specs = {cluster.name: cluster for cluster in clusters}
    _monitor_jobs(specs, jobs, adapter)
    availability = [adapter.scan(cluster) for cluster in clusters]
    active_gpus = sum(job.gpus for job in jobs if _is_running(job.state))
    pending_gpus = sum(job.gpus for job in jobs if _is_pending(job.state))
    actions: list[CoordinatorAction] = []

    if active_gpus >= target_gpus:
        for job in sorted(
            (job for job in jobs if _is_pending(job.state)),
            key=lambda item: item.submitted_at,
            reverse=True,
        ):
            spec = specs.get(job.cluster)
            if spec is None:
                continue
            detail = "target is already met by running allocations"
            if apply:
                adapter.cancel(spec, job.job_id)
                job.state = "CANCELLED"
                job.reason = detail
            actions.append(
                CoordinatorAction(
                    kind="cancel_pending",
                    cluster=job.cluster,
                    job_id=job.job_id,
                    detail=detail,
                    applied=apply,
                )
            )
        pending_gpus = 0
    elif active_gpus + pending_gpus < target_gpus:
        missing_gpus = target_gpus - active_gpus - pending_gpus
        for spec in clusters:
            already_pending = sum(
                1 for job in jobs if job.cluster == spec.name and _is_pending(job.state)
            )
            while missing_gpus > 0 and already_pending < spec.max_pending_jobs:
                detail = f"need {missing_gpus} more GPU(s) to cover target"
                if apply:
                    job_id = adapter.submit(spec)
                    jobs.append(
                        TrackedJob(
                            cluster=spec.name,
                            job_id=job_id,
                            gpus=spec.gpus_per_job,
                            submitted_at=_utc_now(),
                        )
                    )
                    actions.append(
                        CoordinatorAction(
                            kind="submit",
                            cluster=spec.name,
                            job_id=job_id,
                            detail=detail,
                            applied=True,
                        )
                    )
                else:
                    actions.append(
                        CoordinatorAction(
                            kind="would_submit",
                            cluster=spec.name,
                            detail=detail,
                        )
                    )
                missing_gpus -= spec.gpus_per_job
                pending_gpus += spec.gpus_per_job
                already_pending += 1

    return ReconcileReport(
        target_gpus=target_gpus,
        active_gpus=active_gpus,
        pending_gpus=pending_gpus,
        availability=availability,
        actions=actions,
        jobs=list(jobs),
    )


def render_report(report: ReconcileReport) -> str:
    """Render a compact, operator-oriented report."""
    lines = [
        f"Target GPUs: {report.target_gpus}",
        f"Tracked running GPUs: {report.active_gpus}",
        f"Tracked pending GPUs: {report.pending_gpus}",
        "",
        "Cluster availability:",
    ]
    for item in report.availability:
        if item.error:
            lines.append(f"- {item.cluster}: ERROR {item.error}")
        else:
            lines.append(
                f"- {item.cluster}: idle={item.idle_gpus} total={item.total_gpus} "
                f"running_jobs={item.running_gpu_jobs} pending_jobs={item.pending_gpu_jobs}"
            )
    lines.append("")
    lines.append("Coordinator actions:")
    if report.actions:
        for action in report.actions:
            suffix = f" job={action.job_id}" if action.job_id else ""
            mode = "applied" if action.applied else "dry-run"
            lines.append(f"- [{mode}] {action.kind} {action.cluster}{suffix}: {action.detail}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="YAML cluster request configuration")
    parser.add_argument(
        "--state",
        type=Path,
        default=Path("runtime/gpu-capacity-state.json"),
        help="Coordinator-owned job state file (default: runtime/gpu-capacity-state.json)",
    )
    parser.add_argument("--target-gpus", required=True, type=int)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Allow sbatch/scancel for coordinator-owned jobs. Default is dry-run.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the reconciliation report as JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        clusters = load_clusters(args.config)
        jobs = load_state(args.state)
        report = reconcile_capacity(clusters, jobs, args.target_gpus, apply=args.apply)
        save_state(args.state, jobs)
    except CapacityCoordinatorError as exc:
        print(f"gpu-capacity: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.to_jsonable(), indent=2, sort_keys=True))
    else:
        print(render_report(report), end="")
        if not args.apply:
            print("Dry-run only: pass --apply to submit or cancel coordinator-owned pending jobs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
