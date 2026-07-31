#!/usr/bin/env python3
"""Popup provider loopback bridge.

Relays a local login-node port into a Slurm allocation's vLLM server.

Adapted from P124's bridge pattern. Key differences from P124:
- Reads job ID from --job-id argument (never hardcoded)
- Captures srun stderr to a log file (never /dev/null)
- Refuses connections when the allocation is not running
- Auto-reconnects on srun failure by re-querying squeue

Usage:
  python3 bridge.py --job-id 1234567 --remote-port 8000 --local-port 18125 --log bridge.log
"""

from __future__ import annotations

import argparse
import logging
import socket
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [bridge] %(levelname)s %(message)s",
)
log = logging.getLogger("bridge")


def find_job_state(job_id: str) -> str | None:
    """Return the current state of a Slurm job, or None if not found."""
    try:
        result = subprocess.run(
            ["squeue", "-j", job_id, "-h", "-o", "%T"],
            capture_output=True, text=True, timeout=10,
        )
        state = result.stdout.strip()
        return state if state else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def run_srun_overlap(
    job_id: str,
    remote_port: int,
    local_port: int,
    log_path: Path,
) -> int:
    """Run srun --overlap to relay local_port -> remote_port in the allocation.

    Returns the exit code. Never returns 0 unless the connection was
    intentionally closed.
    """
    cmd = [
        "srun", "--overlap", "--jobid", job_id,
        "--export=ALL",
        "python3", "-c", f"""
import socket, sys, time

local_port = {local_port}
remote_port = {remote_port}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', local_port))
server.listen(5)
server.settimeout(1)

log_path = '{log_path}'
conn_count = 0

while True:
    try:
        conn, addr = server.accept()
        conn_count += 1
    except socket.timeout:
        continue

    try:
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect(('127.0.0.1', remote_port))
        remote.settimeout(30)

        def relay(src, dst):
            try:
                while True:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except (socket.timeout, ConnectionResetError, BrokenPipeError):
                pass

        import threading
        t1 = threading.Thread(target=relay, args=(conn, remote), daemon=True)
        t2 = threading.Thread(target=relay, args=(remote, conn), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        remote.close()
    except Exception as e:
        with open(log_path, 'a') as f:
            f.write(f'connection error: {{e}}\\n')
    finally:
        conn.close()
"""
        ]

    with open(log_path, "a") as log_f:
        log_f.write(f"srun --overlap --jobid {job_id} started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.flush()
        proc = subprocess.run(cmd, stdout=log_f, stderr=log_f)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Popup provider loopback bridge")
    parser.add_argument("--job-id", required=True, help="Slurm job ID to bridge into")
    parser.add_argument("--remote-port", type=int, default=8000, help="vLLM port on compute node")
    parser.add_argument("--local-port", type=int, default=18125, help="Local listen port on login node")
    parser.add_argument("--log", type=Path, default=Path("bridge.log"), help="Log file path")
    args = parser.parse_args()

    log.info("Bridge starting: job=%s remote_port=%d local_port=%d",
             args.job_id, args.remote_port, args.local_port)

    # Check allocation is running before accepting connections
    state = find_job_state(args.job_id)
    if state is None:
        log.error("Job %s not found in queue — refusing to bridge", args.job_id)
        return 1
    if state != "RUNNING":
        log.error("Job %s is in state '%s' — not RUNNING. Refusing to bridge.", args.job_id, state)
        return 1

    log.info("Job %s is RUNNING. Starting bridge.", args.job_id)

    # Main relay loop with reconnection
    while True:
        exit_code = run_srun_overlap(args.job_id, args.remote_port, args.local_port, args.log)
        log.info("srun exited with code %d. Checking allocation...", exit_code)

        # Give the allocation a moment, then re-check
        time.sleep(5)
        state = find_job_state(args.job_id)
        if state is None:
            log.error("Job %s no longer in queue. Bridge exiting.", args.job_id)
            return 1
        if state != "RUNNING":
            log.warning("Job %s state: %s. Waiting for RUNNING...", args.job_id, state)
            while state != "RUNNING":
                time.sleep(15)
                state = find_job_state(args.job_id)
                if state is None:
                    log.error("Job %s disappeared. Bridge exiting.", args.job_id)
                    return 1

        log.info("Job %s is RUNNING again. Restarting bridge.", args.job_id)


if __name__ == "__main__":
    sys.exit(main())