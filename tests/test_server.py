"""Tests for the cockpit's server (HANDOFF-0037 §1 and its acceptance test, the server's half).

Purpose: the server binds only to a loopback host; `/api/events` serves the view of the
streams and an event appended by hand appears on the next poll; a summary holding `<script>`
comes back as JSON text with `nosniff`; every method but GET, and every other path, is 404,
including `/` when the page file is absent; the page loads nothing remote and writes no
markup from data, and the Dock files are served; a connection to the machine's LAN address is
refused; a bad query is 400; nothing a request does writes to the streams.
Inputs: streams under `tmp_path`; a server on a free loopback port.
Outputs: pytest assertions.
Side effects: one loopback server per test, stopped after; files under `tmp_path`.
"""

import http.client
import json
import re
import socket
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

from cockpit import server
from kgme import events, ledger

SETTINGS = {"cockpit": {"host": "127.0.0.1", "port": 8642}}
METHODS = ("POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "TRACE", "FROB")


@pytest.fixture
def dirs(tmp_path: Path) -> ledger.Dirs:
    return ledger.Dirs(tmp_path / "ledger", tmp_path / "trace", ("Read",))


@pytest.fixture
def running(dirs: ledger.Dirs) -> Iterator[tuple[str, int]]:
    """Effect: the cockpit on a free loopback port, serving in a thread, closed after."""
    httpd = server.run_bind_server(SETTINGS, dirs, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd.server_address[:2]
    finally:
        httpd.shutdown()
        httpd.server_close()


def request(where: tuple[str, int], method: str, path: str) -> tuple[int, dict, bytes]:
    connection = http.client.HTTPConnection(*where, timeout=5)
    connection.request(method, path)
    response = connection.getresponse()
    body = response.read()
    connection.close()
    return response.status, dict(response.getheaders()), body


def append(dirs: ledger.Dirs, summary: str) -> str:
    return ledger.append(
        events.make_event(
            source="kgme", actor="kgme.test", kind="note", job="test", summary=summary
        ),
        dirs,
    )


@pytest.mark.blocking
def test_the_server_binds_only_to_loopback() -> None:
    assert server.read_bind(SETTINGS) == ("127.0.0.1", 8642)
    assert server.read_bind({}) == ("127.0.0.1", 8642)
    for host in ("::1", "localhost", "127.0.0.2"):
        assert server.read_bind({"cockpit": {"host": host, "port": 1}})[0] == host
    for host in ("0.0.0.0", "192.168.1.20", "::", "example.com"):
        with pytest.raises(ValueError, match="loopback"):
            server.read_bind({"cockpit": {"host": host, "port": 1}})


@pytest.mark.blocking
def test_events_are_served_and_an_appended_event_appears_on_the_next_poll(
    running, dirs: ledger.Dirs
) -> None:
    first = append(dirs, "the first")
    status, headers, body = request(running, "GET", "/api/events")
    view = json.loads(body)
    assert status == 200 and headers["Content-Type"] == "application/json"
    assert [row["id"] for row in view["events"]] == [first] and view["cursor"] == first
    second = append(dirs, "appended by hand")
    _, _, body = request(running, "GET", f"/api/events?since={view['cursor']}")
    assert [row["id"] for row in json.loads(body)["events"]] == [second]


@pytest.mark.blocking
def test_a_script_summary_comes_back_as_text(running, dirs: ledger.Dirs) -> None:
    append(dirs, "<script>alert(1)</script>")
    _, headers, body = request(running, "GET", "/api/events")
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert json.loads(body)["events"][0]["summary"] == "<script>alert(1)</script>"


@pytest.mark.blocking
@pytest.mark.parametrize("method", METHODS)
def test_every_method_but_get_is_404(running, method: str) -> None:
    for path in ("/", "/api/events", "/manifest.json"):
        assert request(running, method, path)[0] == 404, (method, path)


@pytest.mark.blocking
def test_unknown_paths_and_the_unbuilt_page_are_404(running, monkeypatch, tmp_path: Path) -> None:
    for path in ("/x", "/api", "/api/events/x", "/render.py", "/../kgme.toml", "/?x=1"):
        assert request(running, "GET", path)[0] == 404, path
    monkeypatch.setattr(server, "HERE", tmp_path)
    assert request(running, "GET", "/")[0] == 404, "no page until index.html is built"
    (tmp_path / "index.html").write_text("<!doctype html><title>t</title>")
    status, headers, body = request(running, "GET", "/")
    assert status == 200 and headers["Content-Type"].startswith("text/html") and b"<title>" in body


@pytest.mark.blocking
@pytest.mark.parametrize("query", ["stream=all", "limit=0", "limit=501", "limit=x"])
def test_a_bad_query_is_400(running, query: str) -> None:
    assert request(running, "GET", f"/api/events?{query}")[0] == 400


@pytest.mark.blocking
def test_requests_never_write_the_streams(running, dirs: ledger.Dirs) -> None:
    append(dirs, "one line")
    before = sorted((p.name, p.read_bytes()) for p in dirs.ledger.glob("*"))
    for method in ("GET", "POST", "PUT", "DELETE"):
        request(running, method, "/api/events")
    assert sorted((p.name, p.read_bytes()) for p in dirs.ledger.glob("*")) == before
    assert not dirs.trace.exists() or not any(dirs.trace.iterdir())


def read_lan_address() -> str | None:
    """Effect: this machine's address on its default route (a UDP socket is connected, which
    sends nothing), or None offline."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))
        address = probe.getsockname()[0]
    except OSError:
        return None
    finally:
        probe.close()
    return None if address.startswith("127.") else address


@pytest.mark.blocking
def test_a_connection_to_the_lan_address_is_refused(running) -> None:
    address = read_lan_address()
    if address is None:
        pytest.skip("no LAN address on this machine now")
    with pytest.raises(OSError):
        socket.create_connection((address, running[1]), timeout=3).close()


PAGE = Path(server.__file__).with_name("index.html")


@pytest.mark.blocking
def test_the_page_loads_nothing_remote_and_never_writes_markup_from_data() -> None:
    """HANDOFF-0037 §3: no remote asset (ADR-017), and event text only ever as text."""
    page = PAGE.read_text()
    assert not re.search(r"(src|href)\s*=\s*[\"']?(https?:)?//", page), "a remote asset"
    assert "@import" not in page and "url(http" not in page
    for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
        assert sink not in page, sink
    assert "POLL_MS = 2000" in page and "/api/events" in page


@pytest.mark.blocking
def test_the_dock_files_are_served(running) -> None:
    status, headers, body = request(running, "GET", "/manifest.json")
    manifest = json.loads(body)
    assert status == 200 and manifest["start_url"] == "/" and manifest["display"] == "standalone"
    assert [icon["src"] for icon in manifest["icons"]] == ["/icon.png"]
    status, headers, body = request(running, "GET", "/icon.png")
    assert status == 200 and headers["Content-Type"] == "image/png"
    assert body[:8] == b"\x89PNG\r\n\x1a\n"
    status, headers, body = request(running, "GET", "/")
    assert status == 200 and b'rel="manifest"' in body and b'rel="apple-touch-icon"' in body
