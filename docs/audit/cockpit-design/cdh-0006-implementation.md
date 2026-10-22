---
id: AUDIT-CDH-0006
type: report
created: 2026-10-12T18:02:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0006
  - docs/audit/cockpit-design/cdh-0004-cowork-verification.md
  - docs/design/cockpit-v0/ at a27d2f2
  - logs/scratch/design-review/cdh-0006/
tier: 2
status: final
handoff: CDH-0006
period: "2026-10-12"
reviewed_sha: a27d2f2
source_set_digest: eb8002d68811360f347c683fd02ae0e11906b023b33fed5b251a2d5ec592f43b
review_canvas: "private review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, version 1791852068-49df"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| — | — | — | None new. CW7 resolved: the 51 holes inside `<x-dc>` are `{{…}}`, the logic block byte-identical to CDH-0003's. CW8 applied: `.sprite-xscroll` wrappers with `overflow-x:auto` and `min-width` around the matrix and the palette grid (a first attempt reused the outer region's `.sprite-scroll` class and was corrected before commit). CW9 applied: `chibi/README.md` and the fixture footer describe the native board. | — |

### Verdict

PASS

### Notes

**Delivered** on branch `design` as `a27d2f2` (`design: board 10 holes as {{ }}, narrow-width scroll boxes, harness text (CDH-0006)`). Source-set digest over the same 17 paths as AUDIT-CDH-0003: `eb8002d68811360f347c683fd02ae0e11906b023b33fed5b251a2d5ec592f43b`. Changed files:

| Path | SHA-256 |
|---|---|
| `docs/design/cockpit-v0/Sprites.dc.html` | `e54f58bfd3dd315d0e82830587008be202b761f6c7593b5e7d344f433683ca7a` |
| `docs/design/cockpit-v0/canvas.json` | `650393ca46d84101dd9a4c3655aa727202cb9315176aeb7d69cea40b88c0de80` |
| `docs/design/cockpit-v0/chibi/README.md` | `58215297735ac7827b4f9fd6250adba22b314204be02d2a08c3190f60f06792d` |
| `docs/design/cockpit-v0/chibi/preview.html` | `2681c521c3de5091b82f4cb1c829071d4f3be8e60c54fb0a6e1c1d19561aff23` |

`tests/test_design_sprites.py`: 14 passed. `kgme lint`: 0 blocking.

**Observed natively** in the review copy after republishing the committed files (which also reset the `calm` tweak the editor had written into the board as `default: true` during CDH-0004): board 10 in Play at its default state — builder, working, sticker — with all 16 buttons, the facts text, and the status line "1 selected visible detail can animate; every other specimen stays static." (`native-board-10-after-fix-default-state.jpg`). **Motion, natively:** two captures of the 72 px detail 600 ms apart differ in 675 pixels inside the jackhammer/arm region, bounding box (27,58)–(61,115) of the 122 px crop, nowhere else (`native-builder-working-72px-frame-a.png`, `-b.png`): the selected detail animates in the editor and the rest of the figure holds still. The matrix, pairs and contexts were observed natively under CDH-0004's experiment, whose board differs from `a27d2f2` only by CW8's wrappers and CW9's text.

**Not re-observed natively:** the matrix at narrow width after CW8 (the inner region could not be scrolled from the pane this session); the change is CSS-only, source-verified, and does nothing at the board's own width. Reduced motion: as before, the macOS setting is not reachable from here.

**Evidence** under `logs/scratch/design-review/cdh-0006/`: `native-board-10-after-fix-default-state.jpg` `db38821a06dd9796d5836c42b7daa31795bdb4851a2abd1659b665da43aff485`; `native-builder-working-72px-frame-a.png` `8955016d79d71e0feda2ca9f78461e60e57b2619bd7bbbb11fa9e7fb7a930437`; `native-builder-working-72px-frame-b.png` `baedc2a82475d495346328361f52958582fbe40cbc77183146e3c4f096c77b51`.

**Next:** CDH-0005, Codex's read-only review of `a27d2f2`, is `ready` in the README's Codex queue. This report is not Michou's design approval; HANDOFF-0036 stays open to his word.
