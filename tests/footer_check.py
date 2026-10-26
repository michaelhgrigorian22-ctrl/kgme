"""HANDOFF-0061 §3 (review cycle 1 F3): the cockpit's key bar stays inside its window.

Purpose: serve this checkout's `cockpit/` over a small temporary ledger, and in Chromium and in
WebKit, at 1440 x 900 and at the installed window's height 1440 x 820, cycle desk, wall and
station and assert that the footer's last key chip (in the station, its own bottom bar's) ends
at or above the viewport's bottom edge. Chromium is Playwright driving the system Chrome, the
library the Playwright MCP brings (docs/toolbox.md); WebKit is Safari through the system's
`safaridriver` (Safari's "Allow remote automation" must be on). Nothing is downloaded. Not
collected by pytest (it needs browsers); run by hand:
`uv run --frozen python tests/footer_check.py`.
Inputs: this checkout's `cockpit/`; Node with Playwright under `~/.npm/_npx/*`; `safaridriver`.
Outputs: one line per engine, size and view; exit 0 when every chip is inside, 1 when one is
not, 2 when an engine cannot run.
Side effects: a temporary ledger; one loopback server; one Chrome and one Safari session.
"""

import glob
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

from cockpit import server
from kgme import events, ledger

SIZES = ((1440, 900), (1440, 820))
VIEWS = ("desk", "wall", "station")
SAFARI_PORT = 4447
# the page measures itself: cycle with `w` to the view, then the last key chip against the viewport
MEASURE = """async (view) => {
  for (let i = 0; i < 4; i++) {
    const v = document.getElementById("hud").className.match(/v-(\\w+)/);
    if (v && v[1] === view) break;
    document.dispatchEvent(new KeyboardEvent("keydown", {key: "w", bubbles: true}));
    await new Promise(r => setTimeout(r, 400));
  }
  await new Promise(r => setTimeout(r, view === "station" ? 4000 : 900));
  let chip, H = innerHeight;
  if (view === "station") {
    const d = document.getElementById("station").contentDocument;
    const k = d.querySelectorAll(".hud.bottom .kbd");
    chip = k[k.length - 1]; H = d.defaultView.innerHeight;
  } else { const k = document.querySelectorAll("#footer .kbd"); chip = k[k.length - 1]; }
  const b = chip.getBoundingClientRect().bottom;
  return {view, chipBottom: Math.round(b), viewport: H, inside: b <= H};
}"""


def write_ledger(root: Path) -> ledger.Dirs:
    """A few runs: one open, one with an open intent, one closed, so every bar has its keys."""
    dirs = ledger.Dirs(root / "ledger", root / "trace", ("Read",))
    for run, job in (("check-a", "tool:Bash"), ("check-b", "tool:Edit")):
        hook = {"source": "claude-code", "actor": "claude-code.hook", "run_id": run, "job": job}
        intent = events.make_event(kind="intent", key=f"{run}-1", summary="check call", **hook)
        first = ledger.append(intent, dirs)
        if run == "check-a":
            ok = events.make_event(
                kind="outcome", status="ok", key=f"{run}-1", ref=first, summary="check ok", **hook
            )
            ledger.append(ok, dirs)
    return dirs


def chromium(url: str) -> list[dict]:
    found = sorted(glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/playwright")))
    if not found:
        raise RuntimeError("no Playwright under ~/.npm/_npx (the Playwright MCP brings it)")
    script = f"""
const {{ chromium }} = require({json.dumps(found[-1])});
(async () => {{
  const browser = await chromium.launch({{channel: "chrome"}});
  const page = await browser.newPage();
  const rows = [];
  for (const [w, h] of {json.dumps(SIZES)}) {{
    await page.setViewportSize({{width: w, height: h}});
    await page.goto({json.dumps(url)});
    await page.waitForTimeout(1500);
    for (const view of {json.dumps(VIEWS)}) {{
      const row = await page.evaluate({MEASURE}, view);
      rows.push({{size: `${{w}}x${{h}}`, ...row}});
    }}
  }}
  await browser.close();
  console.log(JSON.stringify(rows));
}})().catch(e => {{ console.error(e); process.exit(2); }});
"""
    done = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=300)
    if done.returncode != 0:
        raise RuntimeError(f"chromium: {done.stderr.strip()[-400:]}")
    return json.loads(done.stdout.strip().splitlines()[-1])


def webkit(url: str) -> list[dict]:
    def call(method: str, path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"http://127.0.0.1:{SAFARI_PORT}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.loads(res.read())["value"]

    driver = subprocess.Popen(
        ["safaridriver", "-p", str(SAFARI_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    rows = []
    try:
        wanted = {"capabilities": {"alwaysMatch": {"browserName": "safari"}}}
        sid = call("POST", "/session", wanted)["sessionId"]
        try:
            for w, h in SIZES:
                # Safari sizes the window, its bars included; the viewport is what the page reports
                call(
                    "POST", f"/session/{sid}/window/rect", {"width": w, "height": h, "x": 0, "y": 0}
                )
                call("POST", f"/session/{sid}/url", {"url": url})
                time.sleep(1.5)
                for view in VIEWS:
                    script = (
                        "const done = arguments[arguments.length - 1]; "
                        f"({MEASURE})(arguments[0]).then(done);"
                    )
                    row = call(
                        "POST", f"/session/{sid}/execute/async", {"script": script, "args": [view]}
                    )
                    rows.append({"size": f"{w}x{h} window", **row})
        finally:
            call("DELETE", f"/session/{sid}")
    finally:
        driver.terminate()
    return rows


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        dirs = write_ledger(Path(tmp))
        httpd = server.run_bind_server(
            {"cockpit": {"host": "127.0.0.1", "port": 8642}}, dirs, port=0
        )
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{httpd.server_address[1]}/"
        outside = 0
        try:
            for engine, run in (("chromium", chromium), ("webkit", webkit)):
                try:
                    rows = run(url)
                except Exception as error:  # noqa: BLE001 - an engine that cannot run is reported, exit 2
                    print(f"{engine}: cannot run: {error}")
                    return 2
                for row in rows:
                    outside += not row["inside"]
                    print(
                        f"{engine} {row['size']} {row['view']}: chip {row['chipBottom']} "
                        f"/ viewport {row['viewport']}: {'inside' if row['inside'] else 'OUTSIDE'}"
                    )
        finally:
            httpd.shutdown()
            httpd.server_close()
    print(f"footer check: {outside} outside")
    return 1 if outside else 0


if __name__ == "__main__":
    sys.exit(main())
