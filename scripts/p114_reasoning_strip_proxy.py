"""Forward Responses traffic while removing the unsupported reasoning field."""

from __future__ import annotations

import argparse
import http.client
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    upstream: str

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_POST(self) -> None:
        if self.path not in {"/responses", "/v1/responses"}:
            self.send_error(404, "P114 proxy accepts only /responses")
            return
        try:
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400, "malformed request")
            return
        payload.pop("reasoning", None)
        upstream = urlsplit(self.upstream)
        path = f"{upstream.path.rstrip('/')}{self.path.removeprefix('/v1')}"
        headers = {key: value for key, value in self.headers.items() if key.lower() not in {"host", "content-length", "connection"}}
        connection = http.client.HTTPSConnection(upstream.netloc, timeout=120)
        try:
            connection.request("POST", path, body=json.dumps(payload, separators=(",", ":")).encode("utf-8"), headers=headers)
            response = connection.getresponse()
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {"connection", "transfer-encoding", "content-length"}:
                    self.send_header(key, value)
            self.end_headers()
            while chunk := response.read(65536):
                self.wfile.write(chunk)
                self.wfile.flush()
        finally:
            connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--upstream", required=True)
    args = parser.parse_args()
    Handler.upstream = args.upstream.rstrip("/")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
