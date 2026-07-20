import json
import shutil
import subprocess
import uuid
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_p116_supervised_job.ps1"


def test_dry_run_prepares_one_fresh_native_supervised_job(tmp_path: Path) -> None:
    ticket = tmp_path / "ticket.md"
    ticket.write_text("# bounded ticket\n", encoding="utf-8")
    run_id = "p116_supervised_" + uuid.uuid4().hex
    result = subprocess.run([
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
        "-Ticket", str(ticket), "-Root", str(tmp_path), "-RunId", run_id, "-DryRun",
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    record = json.loads(result.stdout)
    try:
        assert record["staged"] is False
        prompt = Path(record["coordinator_prompt"]).read_text(encoding="utf-8")
        manifest = json.loads(Path(record["manifest"]).read_text(encoding="utf-8"))
        assert "fresh native Coordinator" in prompt
        assert "supervision_wait_delta" in prompt
        assert manifest["worker_session_id"] == "worker-placeholder"
        assert manifest["assigned_root"] == str(tmp_path)
    finally:
        shutil.rmtree(Path(record["manifest"]).parents[1])


def test_refuses_ticket_outside_declared_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    ticket = tmp_path / "ticket.md"
    ticket.write_text("outside", encoding="utf-8")
    result = subprocess.run([
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
        "-Ticket", str(ticket), "-Root", str(root), "-RunId", "p116_supervised_test", "-DryRun",
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Ticket must stay within the declared root" in result.stderr
