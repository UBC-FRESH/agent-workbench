from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agent_workbench.cpu_document_scraper import main

class FakeOpenAIHandler(BaseHTTPRequestHandler):
    request_count = 0

    def do_POST(self) -> None:  # noqa: N802
        type(self).request_count += 1
        content_length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(content_length))
        assert request["model"] == "test-model"
        response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "records": [
                                    {
                                        "record_type": "threshold",
                                        "title_or_heading": "Test heading",
                                        "summary": "Test summary",
                                        "entities": ["Test entity"],
                                        "dates": [],
                                        "locations": [],
                                        "methods_or_actions": [],
                                        "constraints_or_thresholds": ["10 units"],
                                        "evidence_quotes": ["Ten units are required."],
                                        "confidence": 0.9,
                                        "warnings": [],
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        }
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


class FallbackOpenAIHandler(FakeOpenAIHandler):
    def do_POST(self) -> None:  # noqa: N802
        type(self).request_count += 1
        content_length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(content_length))
        content = (
            "not valid JSON"
            if request["model"] == "cpu-model"
            else json.dumps(
                {
                    "records": [
                        {
                            "record_type": "decision",
                            "title_or_heading": None,
                            "summary": "Fallback summary",
                            "entities": [],
                            "dates": [],
                            "locations": [],
                            "methods_or_actions": [],
                            "constraints_or_thresholds": [],
                            "evidence_quotes": [],
                            "confidence": 0.5,
                            "warnings": ["CPU extraction failed"],
                        }
                    ]
                }
            )
        )
        response = {"choices": [{"message": {"content": content}}]}
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def test_scraper_checkpoints_and_resumes(tmp_path: Path) -> None:
    text_path = tmp_path / "runtime" / "chunk.txt"
    text_path.parent.mkdir(parents=True)
    text_path.write_text("Ten units are required.", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "document_id": "document-1",
                "chunks": [
                    {
                        "chunk_id": "document-1-c01",
                        "page_start": 1,
                        "page_end": 2,
                        "runtime_text_path": "runtime/chunk.txt",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        profile_path = tmp_path / "cpu.env"
        profile_path.write_text(
            "\n".join(
                [
                    f"AW_SCRAPER_BASE_URL=http://127.0.0.1:{server.server_port}/v1",
                    "AW_SCRAPER_MODEL=test-model",
                    "AW_SCRAPER_TIMEOUT_SECONDS=5",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        output_path = tmp_path / "output.jsonl"
        summary_path = tmp_path / "summary.json"
        command = [
            "--project-root",
            str(tmp_path),
            "--manifest",
            str(manifest_path),
            "--cpu-profile",
            str(profile_path),
            "--output",
            str(output_path),
            "--summary",
            str(summary_path),
        ]
        assert main(command) == 0
        assert main(command) == 0
    finally:
        server.shutdown()
        thread.join()
    entries = [
        json.loads(line)
        for line in output_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert len(entries) == 1
    assert FakeOpenAIHandler.request_count == 1
    assert entries[0]["status"] == "completed"
    assert entries[0]["records"][0]["chunk_id"] == "document-1-c01"
    assert summary["quality"]["completed_chunks"] == 1
    assert summary["protocol"]["unprocessed_jobs"] == 0


def test_scraper_retries_cpu_then_uses_gpu_fallback(tmp_path: Path) -> None:
    FallbackOpenAIHandler.request_count = 0
    text_path = tmp_path / "runtime" / "chunk.txt"
    text_path.parent.mkdir(parents=True)
    text_path.write_text("Fallback test text.", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "document_id": "document-2",
                "chunks": [
                    {
                        "chunk_id": "document-2-c01",
                        "page_start": 1,
                        "page_end": 1,
                        "runtime_text_path": "runtime/chunk.txt",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), FallbackOpenAIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        cpu_profile = tmp_path / "cpu.env"
        gpu_profile = tmp_path / "gpu.env"
        cpu_profile.write_text(
            f"AW_SCRAPER_BASE_URL=http://127.0.0.1:{server.server_port}/v1\n"
            "AW_SCRAPER_MODEL=cpu-model\n",
            encoding="utf-8",
        )
        gpu_profile.write_text(
            f"AW_SCRAPER_BASE_URL=http://127.0.0.1:{server.server_port}/v1\n"
            "AW_SCRAPER_MODEL=gpu-model\n",
            encoding="utf-8",
        )
        output_path = tmp_path / "output.jsonl"
        summary_path = tmp_path / "summary.json"
        assert (
            main(
                [
                    "--project-root",
                    str(tmp_path),
                    "--manifest",
                    str(manifest_path),
                    "--cpu-profile",
                    str(cpu_profile),
                    "--gpu-profile",
                    str(gpu_profile),
                    "--output",
                    str(output_path),
                    "--summary",
                    str(summary_path),
                ]
            )
            == 0
        )
    finally:
        server.shutdown()
        thread.join()
    entry = json.loads(output_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert FallbackOpenAIHandler.request_count == 3
    assert entry["route"] == "gpu_fallback"
    assert [attempt["lane"] for attempt in entry["attempts"]] == ["cpu", "cpu", "gpu"]
    assert summary["quality"]["gpu_fallback_successes"] == 1
