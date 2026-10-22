---
id: AUDIT-CDH-0007
type: report
created: 2026-10-13T15:45:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0007
  - docs/audit/cockpit-design/cdh-0005-design-review.md
  - docs/design/cockpit-v0/ at 5182d6a
  - logs/scratch/design-review/cdh-0007/
tier: 2
status: final
handoff: CDH-0007
period: "2026-10-13"
reviewed_sha: 5182d6a
review_canvas: "private review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, version 1791931057-6ece (22)"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW10 | cosmetic | `Tray.dc.html` sheet, collapsed demos | At 1440 the `stale · 1 waiting · 1 transient · as of 19:52:14` summary did not fit its third of the sheet and was clipped by the panel (`native-board-11-stale-overflow-before-fix-100pct.jpg`). | Fixed before commit: `.tr-demo .tr-sum{white-space:normal}`; the bar in a real header keeps `nowrap`. Re-observed wrapped (`native-board-11-whole-after-fix-38pct.jpg`). |
| CW11 | cosmetic | `canvas.json` Tray entry | The 640 px frame clipped the sheet's rules list; content measures about 900 px at 1440. | Fixed before commit: `h` 940, `$preview` 940, note `s4` moved below. |
| CW12 | advisory | boards 3, 5 headers at 1440 | The header already wrapped to two lines (harnesses and the usage bars on line 2); with the tray on line 2 the Codex Plus bar drops to a third line when the tray's text is long (`2 working · 1 transient · 1 quiet`), not on board 4 (`1 working · 1 blocked`). | Michou's call: accept (the header is `flex-wrap` by design; one line on a wider desk), or set the tray's summary at 12 px, which recovers the line on board 3. Not changed. |
| CW13 | advisory | board 9 header at 2560 | The Wall's non-wrapping header was already over-full before the tray (ledger, session, hook latency and harnesses each wrap to two lines in the old file too, measured in headless Chromium with a fallback mono font: column heights 56 px before and after); the tray narrows those columns without adding a line. | None in this handoff; the Wall header's widths are a board 9 matter. |

### Verdict

PASS

### Notes

**Delivered** on branch `design` as `5182d6a` (`design: active-runs tray, key a (CDH-0007)`). Files:

| Path | SHA-256 |
|---|---|
| `docs/design/cockpit-v0/Tray.dc.html` (new, board 11) | `a414b31eead9b82ce086bdbe1feca38682212749fa4ceb46cc263da6ff0ebab2` |
| `docs/design/cockpit-v0/Main.dc.html` | `304145c4cd9280329799202fa82dc9f004f60598a30ca5f953b52cafad3dd1d3` |
| `docs/design/cockpit-v0/Blocking.dc.html` | `eefd7e7ef27458c2c0626e2937c1739c117eac249374867f860073624c63c72f` |
| `docs/design/cockpit-v0/Pending.dc.html` | `652f9a3b3d26ea47eb4fb79f7eeb5cbf1e65373b4089f6dc93831e391b8c3a55` |
| `docs/design/cockpit-v0/Disconnected.dc.html` | `a49ae7f37b3b10d841070b5ddd6922fc63bbda4f0fa9b7e5eb369eca87248a98` |
| `docs/design/cockpit-v0/Wall.dc.html` | `719bbe0630167574315fe37a63a3869a1401d1bbe2335b3aedb8297544cb16c3` |
| `docs/design/cockpit-v0/Keys.dc.html` | `59f71290673176bf625ac35a7f60e97fd48e491bfe2c1785cecac3aa51c29026` |
| `docs/design/cockpit-v0/Components.dc.html` | `a0d8fa4d0f3124938812e22bbe03961ad5467df82357c838fcdf0f373e4b52d7` |
| `docs/design/cockpit-v0/canvas.json` | `a082ca20ffbb0397227613bdb483df80c869c1893bf0f6501ae9ffa266bf897f` |
| `docs/design/cockpit-v0/chibi/README.md` | `c4059a5ee64560bdcc10e96786882cc92c5ebfbbfc7640efd70c938a99b054e2` |
| `tests/test_design_sprites.py` | `5e811848a5fd6bbcf209f39fa6c9164951a831723e202a29de89fb0c0a182c64` |

`tests/test_design_sprites.py`: 30 passed (7 actors × 2 boards × 2 checks, the tray's chibi CSS byte-equal to board 10's, the tray's crops equal to the SVGs' `data-portrait`). `kgme lint`: 0 blocking.

**What was drawn.** One child component, `Tray.dc.html` (board 11), mounted into the other boards with the editor's `<dc-import name="Tray" …>` and fed by each board's own `trayRuns` sample list. It carries a second copy of board 10's seven `<symbol>`s and chibi CSS (held equal by the drift test) and every class it adds is `tr-` prefixed, so the host boards' rules are untouched.

- *Collapsed* (`view="bar"`): one column after `harnesses` in the top bar of boards 3, 4, 5, 6 and 9, label `active runs · a`, the 24 px phosphor head-crop portraits of the open runs stacked like cards (`#11151c` tiles, 7 px overlap, 1 px ground outline), then the count per lifecycle word in the bar's 14 px type: board 3 `2 working · 1 transient · 1 quiet`, board 4 `1 working · 1 blocked`, board 5 `1 waiting · 1 transient`, board 6 `stale · 1 waiting · 1 transient · as of 19:52:14` (muted, under the page's grey filter), board 9 as board 3. No run: `idle`, muted, no portrait, the slot keeps its place.
- *Expanded* (`view="pane"`): the pane in board 3's detail column (opened with `a`; the aside's copy says how `Enter` on a timeline row behaves instead) and as the second panel of the Wall's first column. One two-line row per open run: portrait · mapping · short run id · lifecycle word (cyan working, amber waiting/transient, magenta blocked) · elapsed · newest event, ellipsised · that event's ADR-016 class chip. Focused row: 1 px cyan outline and surface tint, as the timeline's. Footer: `j k move · Enter jumps to the run · r filter · Esc closes`.
- *States in text:* `quiet 4m` follows the lifecycle word in muted text and the bar counts `1 quiet` (portrait in `waiting`); `stale · … · as of <last event>`; `idle`; class chips as on board 1. Calm (`[data-calm="true"] .chibi{visibility:hidden}`) hides every portrait and keeps every word and the layout. The tray declares no animation: none of its `.chibi` carry `is-animated`; reduced motion changes nothing in it.
- *Lifecycle words, defined on board 11 and board 1:* working = newest event younger than the run's median gap; waiting = newest event is an intent with no outcome (what `o` lists); transient = newest outcome class transient; blocked = newest outcome or note class blocking and no event since; quiet = a working run past its median gap. The definition is the proposal for HANDOFF-0037's `render.py`; it is not in the ledger schema yet.
- *Board 1* gains a full-width section with the component sheet (`view="sheet"`: the three collapsed states live / idle / stale, the expanded anatomy with four rows, the rule list). Board 1 grows from 1300 to 1900 px, so the canvas's second row moved down by 600 px (`canvas.json`: `y` 1760 → 2360 for boards 7–10, title `t2` 1460 → 2060, note `s3` 3320 → 3920); board 11 (1440 × 940) sits at x 7200 beside board 10 with note `s4`.
- *Board 7:* `a` is now a bound (solid) key with the caption `active runs`; the Filter legend gains `a · only open runs: who is working, waiting, transient or blocked · Enter sets r to that run`, worded like `o`'s row; the key was free and collides with nothing. Board 3's footer gains `a runs`.
- *Samples:* real event shapes from the boards' own ledger samples — `c70d687b…8447` (claude-code · HANDOFF-0040), `01M4F8NR…04F` (kgme.review cycle 1, retry after 23:06), `01M38FTP…TYM` (the HANDOFF-0032 halt, board 4), `Bash make canary-agents` (board 5's unmatched intent). The second builder run on boards 3 and 9 (`3f9e21aa…c0d1`, quiet 4m, a second Claude Code session) is the one invented row, to show the quiet state; board 3's timeline is run-filtered (`r` lit), which is why it does not list it.
- *AUDIT-CDH-0005 F2:* `chibi/README.md`'s two CDH-0002 references now point at CDH-0004/0006 and the three `no outcome` cells read `—`, with the sentence that defined `no outcome` reworded to define `—`; one paragraph added on board 11's copy of the symbols. Wording only.
- The handoff's "Do" still says `{…}` holes; the boards use `{{…}}`, the syntax CDH-0006 proved. Noted, not changed (the handoff is Michou's document).

**Observed natively** in the review copy (version 1791931057-6ece (22), the committed files republished):

- **Board 11** at 38 % and 100 %: the three collapsed states (live with three stacked phosphor portraits and `2 working · 1 transient · 1 quiet`; `idle` muted with no portrait; stale with two portraits and the greyed `stale · … · as of 19:52:14`), the expanded pane with five rows (portrait, mapping, run id, lifecycle word in its colour, elapsed, ellipsised event, class chip `OK` / `—` / `BLOCKING` / `BLOCKING` / `OK`, `WORKING · quiet 4m` on the fifth), the focused first row with the 1 px cyan outline, the footer keys, the rules column. `<dc-import>` is not involved on board 11 itself; its `view` tweak defaults to `board`.
- **Board 3** at 50 % and 100 %: the tray column renders through `<dc-import>` in the header after `harnesses` (`ACTIVE RUNS · a`, three portraits, `2 working · 1 transient · 1 quiet`), and the expanded pane renders in the detail column (`ACTIVE RUNS · a · 3 OPEN`, `ESC CLOSES`, three rows, keys, the explanatory copy), both fed by the board's own `trayRuns`; the footer shows `a runs`. The child component mounts twice on one board without a symbol-id conflict.
- **Board 4**: `1 working · 1 blocked` with two portraits inside the magenta frame; the halt stays the board's.
- **Board 5**: `1 waiting · 1 transient` with two portraits.
- **Board 6**: `stale · 1 waiting · 1 transient · as of 19:52:14`, portraits and words greyed with the page.
- **Board 9**: the bar in the header on one line (`2 working · 1 transient · …`) and the expanded pane as the first column's second panel (`3 OPEN`, three rows, keys).
- **Board 1**: the component sheet mounted as a full-width section before the Noise section; the board's content fits the new 1900 px frame with no clipping.
- **Board 7**: `a` drawn solid with the caption `active runs`; the Filter legend's new row reads `only open runs: who is working, waiting, transient or blocked · Enter sets r to that run`.
- No animation anywhere in the tray (no `.chibi` in it carries `is-animated`); the portraits are static in every capture.

**Not observed natively:** the calm tweak with the tray mounted (the Tweaks panel was not opened this session; the rule is the same `[data-calm="true"] .chibi{visibility:hidden}` that CDH-0004 observed on board 10, now inside the child's own root, driven by the parent's `calm` prop); reduced motion (the macOS setting is not reachable from here, and the tray declares no animation); the keys themselves, since the boards are drawings.

**Evidence** under `logs/scratch/design-review/cdh-0007/` (hashes taken on the Mac after delivery, per `PROVENANCE-2026-10-12.md`):

| File | SHA-256 |
|---|---|
| `native-board-11-bar-and-pane-100pct.jpg` | `ac044c38910b256d9ac8ed97f7dee881e73a2cef822dd32965dea52fdc5f5d48` |
| `native-board-11-stale-overflow-before-fix-100pct.jpg` | `acd38acb3bbc9f49faaac7f5a4f868ddd7e944b8abb45cf78853f115cab7b667` |
| `native-board-11-whole-after-fix-38pct.jpg` | `791dfe8d07a559cd169fb8c328db7f9e3364beca49be921328e7f7d88b7fd286` |
| `native-board-3-header-tray-100pct.jpg` | `ef56541ea33d634072a86ae95406741008342494289092fa402f9565478dc099` |
| `native-board-3-detail-pane-100pct.jpg` | `4ec50378dc86a8ed460705420876d868772c230ff96909128025bcc5a2f8c5fa` |
| `native-board-3-whole-50pct.jpg` | `ed1d4f84ffcf07710a249f51eca968af4796037e03d3b6ca33dda7c7db74c105` |
| `native-board-4-blocked-50pct.jpg` | `90ceb1d6d60b01d772c3413dc85b9a80a21aa1c9a65eca33dd6aff91cdc33979` |
| `native-board-5-waiting-50pct.jpg` | `8ee56059f7f89fde19bce5a34871474031a24b3206e7483b89c6288f581ea688` |
| `native-board-6-stale-50pct.jpg` | `d585469e7ac9dec60ab202583d98f18af5c0a3788557fc31b13d3f33eafb377a` |
| `native-board-9-header-50pct.jpg` | `f28cac983ae257039aa706f9d3129f0b01db8cc3afc0fa5bfe7a8396d1b2a270` |
| `native-board-9-tray-column-50pct.jpg` | `7ec8da12c27fbc8a3251430b4380d7b59e35b21228866842ebe69b8ee988436b` |
| `native-boards-1-and-7-50pct.jpg` | `23d8caf981ea7ae8f3feebe9b7e48547a60bbff37936b8f4ef4d764309ebcc80` |

The captures predate the two cosmetic fixes except the one named `after-fix`; the editor also re-saved `Tray.dc.html` once during the session (attribute normalisation only, from an accidental edit-mode entry), and the committed file is the repository's, republished over it.

**Next:** CDH-0008, Codex's read-only review of `5182d6a`, is `ready` in the README's Codex queue. This report is not Michou's design approval; visual acceptance of the tray and HANDOFF-0036 stay open to his word. Open for Michou from the handoff's own text: whether `Enter` in the pane should set the `r` filter (as drawn) or scroll the timeline to the run's newest event and keep the filter.
