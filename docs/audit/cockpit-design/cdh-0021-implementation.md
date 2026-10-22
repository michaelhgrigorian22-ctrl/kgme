---
id: AUDIT-CDH-0021
type: report
created: 2026-10-21T23:32:54-07:00
handoff: CDH-0021
period: "2026-10-21"
source: inferred
sources:
  - CDH-0021
  - AUDIT-CDH-0020-REVIEW
  - docs/design/cockpit-v0/station/index.html
  - logs/scratch/design-review/cdh-0021/
author: codex
status: final
tier: 2
---

# CDH-0021: the phone HUDs take the ground

CW27 is implemented by adding background:var(--ground) to the existing .hud rule inside max-width:720px. This is the station's only change; no board changed. Source base: 0c9f89237eb3be4bdf75322acb1099e1667db873. The delivered station SHA-256 is 45dbb6db88964982430870d00a3ed00246e7a3d151b5ae1e841f466f828dd129; the prior hash was 0a93f8ebdcd91d0dbe869b10fea0360ba855afae192eb962dc055387bfad7a07. Node verifies that this one declaration accounts for the entire source difference, including unchanged markup and JavaScript.

The existing judgement is 2 × 0.3 = 0.6: on phones the HUD's words take precedence over the deck beneath them. It remains listed for the README's approval screen. No new judgement is introduced. The handoff body is unchanged; adoption and closeout are frontmatter only. No new durable lesson was needed beyond the existing cascade and breakpoint checks.

## Verification

The real page was rebuilt with sh logs/scratch/vendor/make-local.sh and served from logs/scratch/vendor/ on 127.0.0.1. The helper's two import-map substitutions were checked byte for byte against the original source for both versions. The repository sample ledger was copied unchanged into the local server's station directory. Three.js is the existing local 0.182.0 package; nothing was fetched.

Headless Chrome/155.0.8059.85 ran with ANGLE/SwiftShader at device scale 1, 700 px viewport height through 720 px and 900 px at 721 and 1440. Both versions loaded station-local.html's equivalent with at=19:52:00&speed=1, waited for the expected summary, then paused using the page's own control. Calm was entered with the c key. All 24 measured states (2 versions × 6 widths × 2 modes) were paused at 19:52:00, with 37 events and six runs. All four captures retain that clock before and after capture.

| Width, px | Both deck HUD backgrounds after | Summary right edge before and after, px | Summary lines | Calm columns | Calm tracks before and after | Horizontal overflow, px |
| --- | --- | --- | --- | --- | --- | --- |
| 320 | rgb(10, 12, 16) | 304.000 | 2 | 1 | 288px | 0 |
| 360 | rgb(10, 12, 16) | 344.000 | 2 | 1 | 328px | 0 |
| 400 | rgb(10, 12, 16) | 362.156 | 1 | 1 | 368px | 0 |
| 720 | rgb(10, 12, 16) | 362.156 | 1 | 1 | 688px | 0 |
| 721 | rgba(0, 0, 0, 0) | 463.172 | 1 | 1 | 649px | 0 |
| 1440 | rgba(0, 0, 0, 0) | 463.172 | 1 | 3 | 446.656px 446.672px 446.656px | 0 |

Both HUDs were transparent in deck mode at all six widths before the change. Afterward, both are rgb(10, 12, 16) at 320, 360, 400 and 720; both remain transparent at 721 and 1440. Calm already used rgb(10, 12, 16) and retains it at every width. Both HUDs have opacity 1 and z-index 6. Their rectangles, every top HUD fact string, both HUDs' complete text, summary rectangles and text-line bounds match before and after at every width in both modes. The summary remains "2 working (1 quiet) · 1 transient". The calm grid retains seven rooms, identical tracks and 0 px horizontal overflow. Seven actor symbols and a sized WebGL canvas load in every page.

All four PNGs were opened. Before captures at 320 and 400 show room chips, crew tags and bubbles behind HUD text; after captures show no deck label through either HUD's box. The deck remains visible only in the intervening band: 75.547 px at 320 and 153.469 px at 400. Labels still occupy coordinates behind the opaque HUD, and animation can change those coordinates; geometric intersection counts in the manifest are diagnostic, not a claim that those labels remain painted over the HUD. The fix changes occlusion, not scene layout. At 721 and above the sole added declaration does not apply.

The first sandbox run could not bind 127.0.0.1 (EPERM); the approved local-only run succeeded. All 24 distinct observed HTTP requests were to the loopback origin, with 0 page exceptions, console errors or failed HTTP responses. Background network features were disabled and external connections pointed at an unreachable proxy.

Repository gate: make check exits 0; **360 passed, 10 deselected in 30.90 s**. Ruff check passes and all 337 Python files pass format checking. Kgme lint reports 201 notes, 0 blocking, 97 advisory and 6 cosmetic. The design audit folder also passes kgme lint with 0 blocking findings; this report has no advisory finding. The first sandbox gate attempt could not open the existing uv cache; the approved offline retry succeeded. After closeout metadata and the README status were written, the whole-tree coherence test passed (1 test, 0.16 s), report-folder lint again had 0 blocking findings, and git diff --check passed. Cowork's native pass and republication are pending. This is a builder's standalone implementation check, not an independent native verdict or Michou's canvas approval.

## Evidence

Captures and the measurement manifest are gitignored under logs/scratch/design-review/cdh-0021/. Hashes below are taken directly from the Mac's files.

| Capture | Viewport, px | SHA-256 |
| --- | --- | --- |
| before-deck-320.png | 320 × 700 | 1c85bb074106573ed707b73e1e3b2ac63cd8ced5d98586dfbaff9fa59be7938a |
| before-deck-400.png | 400 × 700 | 80f9d0fc623eceadb43dfb0d9b28213a895fe5f4b21344c845747ca5e5f3293d |
| after-deck-320.png | 320 × 700 | 6202a1afd8da46c1d24b51378daa2c035018c653ef98df0defa6d91d748051fc |
| after-deck-400.png | 400 × 700 | d5a54030e44c8f4058d28327570af0b8d3eb321aefe90195ef4bab7c8e4bcd3e |

| Check artifact under logs/scratch/design-review/cdh-0021/ | SHA-256 |
| --- | --- |
| verify.mjs | f463db6f616df83073c160ec80261f07afc78b8fa50c50df3e6f62a2bcf2555a |
| inputs.json | 601696f6aad65c9efbb42c5200f70b75ad8cffcf9d54d186ddc9de3ad8825722 |
| manifest.json | b87f025df2ca18bf37adb9d4f45289e0e0d0dd576913d51d18396cb8cbd82830 |

| Input or served file | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/station/index.html | 45dbb6db88964982430870d00a3ed00246e7a3d151b5ae1e841f466f828dd129 |
| logs/scratch/design-review/cdh-0021/station-before.html | 0a93f8ebdcd91d0dbe869b10fea0360ba855afae192eb962dc055387bfad7a07 |
| logs/scratch/vendor/station-before-cdh-0021.html | 69b96d8707fa7146631647b84271d20e525c584fc843ab8eff5bacaf3560e93c |
| logs/scratch/vendor/station-local.html | d18f90636f6712831a56b78f1eec92ea78357f953c2c7a89607142f041592f8d |
| logs/scratch/vendor/make-local.sh | 0c8680b9b8f2a4afff4b2c45bab1fad062fa2b06c0475a952771496d4cc59913 |
| logs/scratch/vendor/package/package.json | e234d004910abe90f3451486d7ca9feaf7b9f4247b24d5a00233ff6e14bb67a0 |
| logs/scratch/vendor/package/build/three.module.js | d835eab0b3bca3fdfd51e2ce7d06911f4a089b08db73cc3cd70fe5e3005a623f |
| logs/scratch/vendor/package/build/three.core.js | 283be43b2229e15f46dac84cd19354ede5f06cac7ffb185e765cfcfb2c1eec90 |
| docs/design/cockpit-v0/station/sample-events.jsonl | 3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644 |
| logs/scratch/vendor/station/sample-events.jsonl | 3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644 |

The initial main ref is ea1737f2cfad0125f5e8bdf2a9d5fdcad18bbde3. Step 1 remains completed by 67bfebb; main was not merged again. The final ref comparison and all delivered file hashes, including this report, are recorded after the commit in the scratch delivery manifest.

| Other delivered file | SHA-256 |
| --- | --- |
| docs/handoff/cockpit-design/2026-10-21-phone-hud-ground.md | 48554b51b7fbd019f2c1df5df1b40b81d3d7bb4c4045d88a74f94803db952ba2 |
| docs/handoff/cockpit-design/README.md | 5a0b437c3402e306dcd4c9e19a003696f7ef3e0043fa4b53ab40aba39832cdae |

The complete make check log is logs/scratch/design-review/cdh-0021/make-check.log, SHA-256 ece7e368df48965a43d7c12a2bcdbf4f2e7a47b9548269b54e8d6ea0c6c3e21c.
