"""The cockpit's server, effects half (HANDOFF-0037 §1): a read-only view over the ledger.

Purpose: serve the page and the events, nothing else. `http.server.ThreadingHTTPServer` bound
to the loopback host and port of `kgme.toml [cockpit]` (refused for any other host), so a
connection to the machine's LAN address is refused by the operating system. Routes:
`GET /` (the page), `GET /api/events?since=<ulid>&limit=<n>&stream=both|ledger|trace`,
`GET /manifest.json`, `GET /icon.png`. Any other method or path is 404. No route writes,
mutates state, or launches a process (`cockpit/manifest.toml`). The Dock icon does not start
the server: `kgme cockpit` starts it by hand, because launchd waits for Phase 3.
Inputs: `kgme.toml [cockpit]`; the ledger and trace streams of the main checkout; the page
files beside this module.
Outputs: HTTP responses; JSON from `cockpit.render.build_view`.
Side effects: listens on one loopback port; reads the streams and this folder's files.
"""

import ipaddress
import json
import time
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from cockpit import render
from kgme import ledger

HERE = Path(__file__).resolve().parent
FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/manifest.json": ("manifest.json", "application/manifest+json"),
    "/icon.png": ("icon.png", "image/png"),
}
STREAMS = ("both", "ledger", "trace")
LIMIT_MAX = 500
LOOPBACK_NAMES = ("localhost",)


def read_bind(settings: dict) -> tuple[str, int]:
    """Pure: the host and port of `kgme.toml [cockpit]`; ValueError for a host that is not
    loopback, so the cockpit is never reachable from the network."""
    section = settings.get("cockpit", {})
    host, port = str(section.get("host", "127.0.0.1")), int(section.get("port", 8642))
    try:
        loopback = ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = host in LOOPBACK_NAMES
    if not loopback:
        raise ValueError(f"kgme.toml [cockpit] host must be loopback, got {host}")
    return host, port


def read_query(query: str) -> tuple[str | None, int, str]:
    """Pure: `since`, `limit` (1 to 500, default 50) and `stream` from a query string;
    ValueError on a bad value."""
    params = parse_qs(query, keep_blank_values=False)
    since = params.get("since", [None])[0]
    stream = params.get("stream", ["both"])[0]
    if stream not in STREAMS:
        raise ValueError(f"stream must be one of {', '.join(STREAMS)}")
    raw = params.get("limit", ["50"])[0]
    if not raw.isdigit() or not 1 <= int(raw) <= LIMIT_MAX:
        raise ValueError(f"limit must be an integer from 1 to {LIMIT_MAX}")
    return since, int(raw), stream


def read_file(path: str) -> tuple[bytes, str] | None:
    """Effect: the bytes and content type of one of the page's files (`/`, `/manifest.json`,
    `/icon.png`) beside this module, or None when the route is not a file or is not built."""
    if path not in FILES:
        return None
    name, content_type = FILES[path]
    found = HERE / name
    return (found.read_bytes(), content_type) if found.is_file() else None


def read_events(dirs: ledger.Dirs, since: str | None, limit: int, stream: str) -> dict:
    """Effect: the streams asked for, read whole (a run's state needs its history), and the
    view `render.build_view` makes of them."""
    ledger_events = ledger.read(dirs, stream="ledger") if stream in ("both", "ledger") else []
    trace_events = ledger.read(dirs, stream="trace") if stream in ("both", "trace") else []
    now_ms = int(time.time() * 1000)
    return render.build_view(ledger_events, trace_events, now_ms, since, limit)


class Handler(BaseHTTPRequestHandler):
    """GET on the four routes; 404 for any other path and for every other method."""

    server_version = "kgme-cockpit"
    dirs: ledger.Dirs

    def __init__(self, *args, dirs: ledger.Dirs, **kwargs) -> None:
        """One request, served by the base class's constructor; `dirs` are the streams read."""
        self.dirs = dirs
        super().__init__(*args, **kwargs)

    def __getattr__(self, name: str):
        """Every `do_<METHOD>` but GET resolves to the 404."""
        # every method but GET: `BaseHTTPRequestHandler` looks up `do_<METHOD>`
        if name.startswith("do_"):
            return self.write_not_found
        raise AttributeError(name)

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - the base class's name
        """Silence: the server keeps no access log (it would be a second record of the reads)."""
        return

    def write_body(self, code: int, body: bytes, content_type: str) -> None:
        """Effect: one response with `body` (headers only for HEAD), never cached or sniffed."""
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def write_not_found(self) -> None:
        """Effect: the 404 every other path and every method but GET receive."""
        self.write_body(404, b"not found\n", "text/plain; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 - the base class's naming
        """Effect: the four routes; `/api/events` reads the streams through `read_events`."""
        url = urlsplit(self.path)
        if url.path == "/api/events":
            try:
                since, limit, stream = read_query(url.query)
            except ValueError as error:
                self.write_body(400, f"{error}\n".encode(), "text/plain; charset=utf-8")
                return
            view = read_events(self.dirs, since, limit, stream)
            self.write_body(200, json.dumps(view).encode(), "application/json")
            return
        found = None if url.query else read_file(url.path)
        if found:
            self.write_body(200, *found)
            return
        self.write_not_found()


def run_bind_server(
    settings: dict, dirs: ledger.Dirs, port: int | None = None
) -> ThreadingHTTPServer:
    """Effect: a bound server, not yet serving; `port` overrides the configured one (0 asks
    the system for a free port, as the tests do)."""
    host, configured = read_bind(settings)
    handler = partial(Handler, dirs=dirs)
    return ThreadingHTTPServer((host, configured if port is None else port), handler)


def run_cockpit(settings: dict, dirs: ledger.Dirs) -> int:
    """`kgme cockpit`: serve until interrupted."""
    server = run_bind_server(settings, dirs)
    host, port = server.server_address[:2]
    print(f"kgme cockpit: serving on http://{host}:{port}/ (Ctrl-C stops it)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
