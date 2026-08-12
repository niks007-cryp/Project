"""
Local HTTP Web Server for Local AI Clipper Control Panel.
Binds to 127.0.0.1 (localhost) serving local REST API and Web Control Panel UI.
"""

import json
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from clipper.web.api import LocalClipperAPI
from clipper.infrastructure.logger import get_logger

logger = get_logger("web_server")


class ClipperHTTPRequestHandler(BaseHTTPRequestHandler):
    """Local HTTP Request Handler for API & Control Panel UI."""

    api = LocalClipperAPI()
    static_dir = Path(__file__).parent / "static"

    def log_message(self, format, *args):
        # Mute standard noisy HTTP server stdout logging
        pass

    def _send_json(self, data: Any, status_code: int = 200):
        origin = self.headers.get("Origin", "*")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Filename")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def do_OPTIONS(self):
        origin = self.headers.get("Origin", "*")
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Filename")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/api/health":
                self._send_json(self.api.get_health_status())
            elif path == "/api/projects":
                self._send_json(self.api.list_projects())
            elif path.startswith("/api/jobs/"):
                job_id = path.split("/")[3]
                self._send_json(self.api.get_job_detail(job_id))
            elif path == "/api/providers":
                self._send_json(self.api.list_providers())
            else:
                # Serve Static Index Control Panel
                index_file = self.static_dir / "index.html"
                if index_file.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    with open(index_file, "rb") as f:
                        self.wfile.write(f.read())
                else:
                    self._send_json({"error": "Control panel index UI file not found."}, status_code=404)
        except Exception as e:
            self._send_json({"error": str(e)}, status_code=500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        try:
            if path == "/api/media/ingest":
                res = self.api.ingest_media(file_path=body.get("file_path"), job_id=body.get("job_id"))
                self._send_json(res)
            elif path == "/api/media/ingest-youtube":
                res = self.api.ingest_youtube(url=body.get("url"), job_id=body.get("job_id"))
                self._send_json(res)
            elif path == "/api/media/upload":
                # Raw file upload handler
                filename = self.headers.get("X-Filename", "upload_media.mp4")
                content_length = int(self.headers.get("Content-Length", 0))
                file_bytes = self.rfile.read(content_length)
                res = self.api.ingest_file_bytes(filename=filename, file_bytes=file_bytes)
                self._send_json(res)
            elif path.startswith("/api/jobs/") and "/run" in path:
                parts = path.split("/")
                job_id = parts[3]
                stage_name = body.get("stage_name")
                options = body.get("options", {})
                res = self.api.run_pipeline_stage(job_id, stage_name, options)
                self._send_json(res)
            elif path == "/api/candidates/review":
                res = self.api.save_human_review(
                    job_id=body.get("job_id"),
                    candidate_id=body.get("candidate_id"),
                    status_action=body.get("action")
                )
                self._send_json(res)
            elif path == "/api/providers/set":
                res = self.api.set_provider_credential(
                    provider_name=body.get("provider_name"),
                    api_key=body.get("api_key"),
                    model_name=body.get("model_name", "default")
                )
                self._send_json(res)
            elif path == "/api/providers/test":
                res = self.api.test_provider_connection(provider_name=body.get("provider_name"))
                self._send_json(res)
            else:
                self._send_json({"error": "Unknown API endpoint"}, status_code=404)
        except Exception as e:
            self._send_json({"error": str(e)}, status_code=500)


def start_local_web_server(host: str = "127.0.0.1", port: int = 3000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, ClipperHTTPRequestHandler)
    logger.info(f"Local AI Clipper Web Control Panel started at http://{host}:{port}")
    print(f"==========================================================")
    print(f"  LOCAL AI CLIPPER CONTROL PANEL STARTED                  ")
    print(f"  URL: http://{host}:{port}                               ")
    print(f"  Binding: {host} (Localhost Only)                        ")
    print(f"==========================================================")
    return httpd
