---
id: AUDIT-CDH-0019-CYCLE-1
type: report
created: 2026-10-21T13:03:52-07:00
handoff: CDH-0019
period: "2026-10-21"
source: inferred
sources:
  - CDH-0019
  - AUDIT-CDH-0018
  - AUDIT-CDH-0016
  - docs/design/cockpit-v0/
  - logs/scratch/design-review/cdh-0019-cycle-1/
author: codex
status: final
tier: 2
---

# CDH-0019 cycle 1: duration contrast and the narrow calm grid

This implementation acts on the latest review, AUDIT-CDH-0018 at 2e14d66, under the standing mandate. Source base: 479816c0ac12cbc1e5ce87e0ca2f72616c9a2134. The cycle changes three design files and updates status, two measurement lessons and the handoff-author boundary lesson. Its commit parent is ebcb84759836b3ed3ae313768c7588965969e770, where the handoff author committed the adoption stamp and corrected its five references; the design source is identical to the measured base. Cowork supplies the independent native verdict; this report records builder checks, not self-approval.

| Finding | Disposition | Evidence and score |
| --- | --- | --- |
| AUDIT-CDH-0018 F1, blocking | Fixed in Main and Wall: duration spans use class mut, with only alignment inline. | Local Chrome computed styles change #6f8290 to #7a8d9b on #0e1a22, from 4.4317357:1 to 5.1371408:1. This is a check, not a judgement call. |
| AUDIT-CDH-0018 F2, advisory | Built: the grid minimum is min(400px,100%). | Stakes 2 × edge 0.1 = 0.2. The narrow track fits available width; the existing wider layouts are unchanged. No approval-screen addition is required below 0.5. |
| CW25, existing cosmetic observation | Accepted pending native observation; no geometry patch. | Stakes 1 × edge 0.2 = 0.2. The supplied one-pixel edge touch does not justify another bubble-position patch. |

F1 is the first patch to the missed duration spans. CDH-0017 changed the other muted cells; this cycle neither repeats that diff nor attempts a third repair. The other boards' duration colors already pass at 4.6681 and 4.5583:1 and are unchanged. No finding is disputed. Historical reviews and implementation reports remain intact.

## Verification

The CSS fixture extracts the actual style blocks and duration markup from the source base and delivered files. It uses four duration frames and fourteen grid frames with seven labelled synthetic room cards. It excludes editor support scripts, remote fonts and the station module. On this arm64 Mac running macOS 26.6.2, installed HeadlessChrome/155.0.0.0 runs the local fixture with a fresh scratch profile, background network features disabled, an unreachable proxy and a content-security policy excluding external resources. The first sandboxed Chrome launch aborted with exit 134 before producing DOM; the approved retry succeeded. This is isolated CSS verification, not an import into the native editor or a full station render.

Both duration frames resolve to rgb(122,141,155) on rgb(14,26,34), versus the baseline rgb(111,130,144). Node calculates WCAG contrast from the browser's computed values using linearized sRGB. Both pass 4.5:1. Alignment remains right-aligned in source.

| Frame viewport | Before track | After track | After columns | Before/after wall scroll excess |
| --- | --- | --- | --- | --- |
| 320 px | 400 px | 288 px | 1 | 96 / 0 px |
| 360 px | 400 px | 328 px | 1 | 56 / 0 px |
| 400 px | 400 px | 368 px | 1 | 16 / 0 px |
| 720 px | 688 px | 688 px | 1 | 0 / 0 px |
| 721 px | 649 px | 649 px | 1 | 0 / 0 px |
| 1440 px | 446.656 / 446.672 / 446.656 px | Identical | 3 | 0 / 0 px |
| 2560 px | 403 px | 403 px | 6 | 0 / 0 px |

The media breakpoint changes padding between 720 and 721 px. Scroll excess here is wall.scrollWidth minus wall.clientWidth; the review's 112/72/32 px figures instead measured track width minus grid content width. Their 16 px difference is the wall's inset, not conflicting evidence. These seven fixture results establish the grid correction only; full station text, HUD and viewport containment remain native follow-up work.

The current page's extracted functions pass the Node regression checks: an ordinary bookkeeping note preserves the halt; intent, outcome and approval resume it; all five null-parent root intents wait; an ordinary 390-second median triggers quiet strictly after the threshold; a hidden zero-size stage performs no camera or renderer writes; visible 1200 by 800 and 360 by 700 resizes restore finite camera bounds and all four render targets; leaving calm calls resize; pause freezes replay time without a resume jump; five character shortcuts ignore editable targets. The script also revalidates all 38 historical delivery hashes used by CDH-0016. Its results are saved with the exact script. No station JavaScript changed in this cycle.

Full repository gate after author commit ebcb847: **360 passed, 10 deselected in 29.69 s**, exit 0. Ruff check and format pass; kgme lint reports 195 notes, 0 blocking, 91 advisory and 6 cosmetic. The whole-tree coherence test passes. The earlier offline run passed 359 tests and failed only coherence on five references in the newly open handoff. Its author applied the prepared correction unchanged and committed it; Codex did not edit the handoff body, and no exception to that boundary was granted. The earlier sandbox run also failed two temporary-repository hook tests, which passed on the approved offline retry. Historical logs remain below. Native pixels, clicks, focus and performance remain unverified by Codex. The station is **unverified standalone** because logs/scratch/vendor/ and the local three@0.182.0 package are absent. No package was fetched. No new raster capture was made; the browser evidence is text DOM, computed styles and dimensions.

## Delivery and evidence

These are all five changed payload files; this report is the sixth delivery file. Its own hash cannot be embedded in itself; the scratch delivery manifest identifies it after finalization. The single cycle commit is titled "design: fix duration contrast and narrow calm grid (CDH-0019)". The handoff belongs to author commit ebcb847 and is excluded from this cycle's pathspec.

| File | SHA-256 |
| --- | --- |
| `docs/design/cockpit-v0/Main.dc.html` | `9530b4bbebec1eac1cede407a672d55ebce6cc9370150bf50dd7ea1132228ddc` |
| `docs/design/cockpit-v0/Wall.dc.html` | `6730cb1245c68d4629c80ff5eb8b00c5fa3aa92b0d220e790338067879391413` |
| `docs/design/cockpit-v0/station/index.html` | `35f87569802e1b16e8610dce451c15c9ee84364e33eb072c1870d1952e7952bc` |
| `docs/readers/cockpit-design-lessons.md` | `05c4b312661f2af71657bfa40fc2d78374d0864cd294f7aeab7a4af405664ae2` |
| `docs/handoff/cockpit-design/README.md` | `b023b50487f385caa1d4be360846dc250599c9bae4273515040482c32581a8d6` |

The six evidence files below remain gitignored. They contain only the isolated fixture and local check output; no binaries are committed.

| File | SHA-256 |
| --- | --- |
| `logs/scratch/design-review/cdh-0019-cycle-1/css-fixture.html` | `efd0404edd0776ffa7e582426160942f82334628fa49f1878a044914e782203a` |
| `logs/scratch/design-review/cdh-0019-cycle-1/css-dom.html` | `e3c0bcf4e0d5cd9f14a217dad7740fb13750612209c2bdb3b01fbab681fb4f79` |
| `logs/scratch/design-review/cdh-0019-cycle-1/css-checks.json` | `14b9487d6cf8f9668aaa1b6e1481bf588409c92929e509e170ae30d032f67aec` |
| `logs/scratch/design-review/cdh-0019-cycle-1/check-source.mjs` | `a2dcf5d7da371b70bbddd49d8d846d95a5f3d5ce1b82c3bd0d1fad50a4bdc949` |
| `logs/scratch/design-review/cdh-0019-cycle-1/source-checks.json` | `b9b9e37d0f5233376b3eec8e6d3685b715c3c14a63c1e01535aa706ab7434d5d` |
| `logs/scratch/design-review/cdh-0019-cycle-1/node-check.log` | `9f26fffd2928a09de2237e1bb847c4a2a89e066ac2d50be2c1d37ffb0b795a9a` |

## Queue, merge and decisions

CDH-0016 is done in d649f08 and CDH-0018 is done in 479816c. CDH-0019 is adopted from Michou and stays open across cycles; no ready row remains. The README now states CW17's partial prior repair and the new duration fix, retains the 0.6 wide-grid preference, and records this cap at 0.2. The lessons file remains at most 40 lines.

The merge is 67bfebb1106e4ea8ab9de1617727d759795e3a40. Its gate passed 360 tests, with 10 agent tests deselected and zero blocking lint findings. The gitignored labelled logs/scratch/review.patch placeholder and runtime logs/trace/ directory satisfy the current coherence check; the runtime-output dependency defect is routed to the substantive session. Michou should repoint kgq to control/review/codex-builder-prompt.md.

The start-of-run main SHA was f8cad6c9c1e3d1a16a2d62af3d33040f55ee5e61. Main advanced independently during the session; the merge took 9b166b6c53460495e9d09c13eb89f48478ad5760. This session did not commit, check out or push main. At the previous stop main was 04fe8416681841222abbb30506e596e7532a8cb1. This closeout records the newer 4ccb919055cd1270ccf854d64fc4f833f689ba53 as its baseline. Both advances were external; no second merge was attempted. The closing message confirms the final comparison.

The three existing judgement questions remain unanswered: station direction, 4 × 0.7 = 2.8, recommendation keep and iterate; joins or replaces the wall, 4 × 0.6 = 2.4, recommendation joins with w cycling desk, wall, station; bridge likeness, 3 × 0.8 = 2.4, recommendation retain the chalk silhouette. The asked-and-answered line and taken-recommendation tally are unchanged. Cowork republishes and reviews this build natively after delivery; nothing is marked complete on its behalf.

Additional gate and proposal evidence, all gitignored:

| File under logs/scratch/design-review/cdh-0019-cycle-1/ | SHA-256 |
| --- | --- |
| `make-check.log` | `e9985e3f54bb44cb0777280f87b908db99dbc08f7478097067d359b29bd6138a` |
| `make-check-retry.log` (final passing gate) | `88ea225bed2a7fc13fb531f56dc565e565ef870a98858ea3ddf7a65223eb8ef8` |
| `make-check-before-author-fix.log` | `2621c0ae4bf67207699f93186401daadc5373ca1958c2473d5fc580b86e83b40` |
| `coherence-check.log` | `6518e4fe5683dd263b5edc4bddcccf14385b3d9d6d035444a576f2f8b16d06e5` |
| `proposed-handoff-paths.patch` | `273923ee12011e4e4eb2626229979374616a8cbdba6d405b80ff3ac9833f8b8f` |

Before the author correction, the proposed patch passed git apply --check and its body substituted in memory changed five coherence findings to zero. On closeout, the committed handoff matches that proposed text byte for byte. proposal-check.json SHA-256: 43acbec64c77eaf16bd5b8475e830efa0a9fb9dd0c307672ab2e8869fd862578.
