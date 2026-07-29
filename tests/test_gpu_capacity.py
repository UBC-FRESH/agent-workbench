from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

import pytest

from agent_workbench.gpu_capacity import (
    ClusterSpec,
    SlurmOverSsh,
    TrackedJob,
    load_clusters,
    load_state,
    reconcile_capacity,
    save_state,
)


class FakeRunner:
    def __init__(self, responses: dict[str, str]) -> None:
        self.responses = responses
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str]) -> CompletedProcess[str]:
        self.commands.append(command)
        remote = command[-1]
        for needle, stdout in self.responses.items():
            if needle in remote:
                return CompletedProcess(command, 0, stdout, "")
        return CompletedProcess(command, 1, "", f"unexpected command: {remote}")


def _cluster(name: str = "alpha", gpus_per_job: int = 4, max_pending_jobs: int = 1) -> ClusterSpec:
    return ClusterSpec(
        name=name,
        ssh_target=f"user@{name}.example.edu",
        submission_script="/scratch/user/request_gpu.sh",
        gpus_per_job=gpus_per_job,
        partition="gpu",
        account="project",
        constraint="gpu_mem_32",
        max_pending_jobs=max_pending_jobs,
    )


@pytest.mark.smoke
def test_reconcile_dry_run_plans_cross_cluster_submissions() -> None:
    alpha = _cluster("alpha", gpus_per_job=4)
    beta = _cluster("beta", gpus_per_job=2)
    runner = FakeRunner(
        {
            "squeue -h -j": "",
            "sinfo -N": "a01|idle|gpu:v100:4\n",
            "squeue -h -t": "",
        }
    )

    report = reconcile_capacity(
        [alpha, beta], [], 6, apply=False, adapter=SlurmOverSsh(runner)
    )

    assert report.active_gpus == 0
    assert report.pending_gpus == 6
    assert [(action.kind, action.cluster) for action in report.actions] == [
        ("would_submit", "alpha"),
        ("would_submit", "beta"),
    ]
    assert not any("sbatch" in command[-1] for command in runner.commands)


@pytest.mark.smoke
def test_reconcile_apply_submits_and_tracks_jobs() -> None:
    alpha = _cluster()
    runner = FakeRunner(
        {
            "squeue -h -j": "",
            "sinfo -N": "a01|idle|gpu:v100:4\n",
            "squeue -h -t": "",
            "sbatch --parsable": "81234;cluster\n",
        }
    )
    jobs: list[TrackedJob] = []

    report = reconcile_capacity([alpha], jobs, 4, apply=True, adapter=SlurmOverSsh(runner))

    assert report.actions[0].kind == "submit"
    assert report.actions[0].job_id == "81234"
    assert jobs[0].job_id == "81234"
    assert jobs[0].gpus == 4
    assert any("sbatch --parsable" in command[-1] for command in runner.commands)


@pytest.mark.smoke
def test_reconcile_cancels_only_tracked_pending_jobs_after_target_lands() -> None:
    alpha = _cluster()
    jobs = [
        TrackedJob("alpha", "100", 4, "2026-07-29T00:00:00+00:00"),
        TrackedJob("alpha", "101", 4, "2026-07-29T00:01:00+00:00"),
    ]
    runner = FakeRunner(
        {
            "squeue -h -j": "100|RUNNING|node01\n101|PENDING|Priority\n",
            "sinfo -N": "a01|mix|gpu:v100:4\n",
            "squeue -h -t": "100|RUNNING|gres/gpu:4|node01\n",
            "scancel 101": "",
        }
    )

    report = reconcile_capacity([alpha], jobs, 4, apply=True, adapter=SlurmOverSsh(runner))

    assert report.active_gpus == 4
    assert report.pending_gpus == 0
    assert jobs[0].state == "RUNNING"
    assert jobs[1].state == "CANCELLED"
    assert [(action.kind, action.job_id) for action in report.actions] == [("cancel_pending", "101")]
    assert any("scancel 101" in command[-1] for command in runner.commands)
    assert not any("scancel 100" in command[-1] for command in runner.commands)


@pytest.mark.smoke
def test_reconcile_dry_run_never_cancels_pending_jobs() -> None:
    alpha = _cluster()
    jobs = [
        TrackedJob("alpha", "100", 4, "2026-07-29T00:00:00+00:00"),
        TrackedJob("alpha", "101", 4, "2026-07-29T00:01:00+00:00"),
    ]
    runner = FakeRunner(
        {
            "squeue -h -j": "100|RUNNING|node01\n101|PENDING|Priority\n",
            "sinfo -N": "a01|mix|gpu:v100:4\n",
            "squeue -h -t": "100|RUNNING|gres/gpu:4|node01\n",
        }
    )

    report = reconcile_capacity([alpha], jobs, 4, apply=False, adapter=SlurmOverSsh(runner))

    assert jobs[1].state == "PENDING"
    assert [(action.kind, action.applied) for action in report.actions] == [
        ("cancel_pending", False)
    ]
    assert not any("scancel" in command[-1] for command in runner.commands)


@pytest.mark.smoke
def test_monitor_marks_jobs_unknown_when_scheduler_is_unreachable() -> None:
    alpha = _cluster()
    jobs = [TrackedJob("alpha", "100", 4, "2026-07-29T00:00:00+00:00")]
    runner = FakeRunner(
        {
            "sinfo -N": "a01|idle|gpu:v100:4\n",
            "squeue -h -t": "",
        }
    )

    report = reconcile_capacity([alpha], jobs, 4, apply=False, adapter=SlurmOverSsh(runner))

    assert jobs[0].state == "UNKNOWN"
    assert report.active_gpus == 0


@pytest.mark.smoke
def test_cluster_config_and_state_round_trip(tmp_path: Path) -> None:
    config_path = tmp_path / "clusters.yaml"
    config_path.write_text(
        """clusters:
  - name: alpha
    ssh_target: user@alpha.example.edu
    submission_script: /scratch/user/request.sh
    gpus_per_job: 1
""",
        encoding="utf-8",
    )
    specs = load_clusters(config_path)
    state_path = tmp_path / "state.json"
    jobs = [TrackedJob("alpha", "81234", 1, "2026-07-29T00:00:00+00:00")]

    save_state(state_path, jobs)

    assert specs[0].name == "alpha"
    assert load_state(state_path) == jobs
