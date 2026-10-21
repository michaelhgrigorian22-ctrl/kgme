---
id: AUDIT-CDH-0018
type: report
created: 2026-10-21T01:30:58-07:00
handoff: CDH-0018
period: "2026-10-21"
source: inferred
sources:
  - CDH-0018
  - AUDIT-CDH-0017
  - AUDIT-CDH-0016
  - ADR-016
  - ADR-017
  - docs/readers/cockpit-design.md
  - control/review/design-prompt.md
  - control/review/design-reference/ui-ux-pro-max/
  - docs/design/cockpit-v0/ at 2e14d66a2cb1584ece0f0f3cd76edde97e2193cd
  - docs/handoff/cockpit-design/README.md at 2e14d66a2cb1584ece0f0f3cd76edde97e2193cd
  - logs/scratch/design-review/cdh-0017/
  - logs/scratch/design-review/cdh-0018/
author: codex
status: final
tier: 2
reviewed_sha: 2e14d66a2cb1584ece0f0f3cd76edde97e2193cd
---

## Findings

CW18 is closed and CW22 has an explicit source minimum. CW17 is only partially closed: its time and job fields now pass, but the duration field bypasses the new class. Paths below are relative to docs/design/cockpit-v0/.

| id | class | file:line | finding | fix |
| --- | --- | --- | --- | --- |
| F1 | blocking | Main.dc.html:156; Wall.dc.html:125 | The elapsed cell still has inline `text-align:right;color:#6f8290`, with no mut class. On the cyan-focused row's #0e1a22 background it remains 4.4317:1, below 4.5:1. The selected transient row actually displays this cell. The new .focus .mut rule repairs the time and job fields, not duration; CDH-0017's all-three-fields claim is therefore false. | Give these two duration spans class mut and retain only text-align in their inline style. Their focused text then uses #7a8d9b at 5.1371:1. |
| F2 | advisory | station/index.html:99, #wall .grid | The new fixed 400 px grid minimum exceeds the calm wall's inner width at narrow viewports: by 32 px at 400, 72 px at 360 and 112 px at 320. The wall permits scrolling, so this is an avoidable narrow-layout regression rather than established loss of facts. | Cap the minimum to available width with minmax(min(400px,100%),1fr). Preserve the 400 px desktop preference and the existing gap. |

## Verdict

BLOCK: 1 blocking finding at 2e14d66; CW17's duration cells remain below the text-contrast gate.

## Notes

**Source and scope.** Review of Michael Grigorian's 2e14d66a2cb1584ece0f0f3cd76edde97e2193cd, not a Codex-authored build. The 26-file design snapshot has source-set SHA-256 `90f6d0e8d087c1ffafd8e3077889675a8e08bf507f94980eed26e1ce87e923d7`, calculated from sorted repository-path, NUL, file-hash, LF records. Seven design files differ from d2f1d29; their hashes are below. Canvas order, cast geometry, shared animation code, keyboard map, tray, sample events and lifecycle functions are unchanged. AUDIT-CDH-0016 records their source checks, supplied cast profiles, sample validation and remaining native limitations. This pass concentrates on the seven-file diff and supplied CDH-0017 evidence; it does not claim a new native or performance run. The merge gate passed 360 tests before these read-only reviews.

| Changed design source | SHA-256 |
| --- | --- |
| `Main.dc.html` | `b2010aef6498bf452b99fe574ad65fd841f1229e38d1f17d52073399163d4017` |
| `Blocking.dc.html` | `ec2c61c00c4bcc085a78f77e0c1628807c42acd5ec844dae673890cac06f7b6e` |
| `Pending.dc.html` | `15cb75b53c47267ff85689e0646a1cff068581f82c8cfd2dab5176e523e414da` |
| `Wall.dc.html` | `e939782d18b31c7e3826d836d6a658f8fd3979f6891c5c8636b3f016000833cb` |
| `Disconnected.dc.html` | `4e13f38b0113f91be1b316820193d6d45b79220e4e2b975a6e0480e0f8f03592` |
| `station/index.html` | `e14eac978ef4c3f4db9a28a61e2181a698683d62bed3b8da08ae24c09156d67c` |
| `station/README.md` | `ddccdff36108a52c13855b40fb4095fdd0a1576a0f997b23c6edd2efc5afffc9` |

**Three checks.** Independent contrast arithmetic follows the actual inline and class declarations. Focused .mut text passes on Main/Wall, Blocking and Pending at 5.1371, 5.4112 and 5.2839:1 respectively. All four duration spans retain inline #6f8290; only Main/Wall fail. Blocking's duration is 4.6681:1 and Pending's is 4.5583:1, so F1 does not require changing their tints or durations.

The disconnected host now uses #a3b0b8 for its muted text. After saturate(.12) brightness(.72), its contrast is 4.7640:1 against the ground and 4.6703:1 against the filtered panel. The host's prefixed .stale .tr-root rules override the mounted tray's muted labels, run identifiers, metadata, quiet suffix, footer and empty state. The tray's existing #cfe6ef stale summary remains 7.7166:1 against the ground. This closes CW18 and AUDIT-CDH-0016 F2 in source; native compositing is not newly observed.

All eight filter buttons across Main and Blocking inherit the new explicit min-height:24px; their text, keycaps and padding make their widths exceed 24 px. Pending and Wall add no filter buttons. CW22's source now supports a 24 by 24 minimum without the earlier spacing exception. Actual native boxes remain Cowork's measurement, not a fresh Codex observation.

**Four builds.** Bubbles now sit below the crew wrapper at top:calc(100% + 16px), with their arrow above. The supplied refusal and note captures show that placement. The manifest reports 10 visible-bubble checks across three moments and one edge overlap; AUDIT-CDH-0017 identifies it as one pixel, CW25. Keep that limitation: neither the samples nor the source justify a universal no-overlap claim. The note image was captured after the measurement and shows fewer surviving bubbles, consistent with the recorded replay advance and finite bubble lifetime.

The HUD uses hullText, while the calm wall uses hullLong. Independent evaluation of the source snapshot function with a synthetic active halt returns `HALT · halt:review:test` and `HALT · full halt sentence` respectively. The two halt captures show the intended short key and full sentence. Escaping remains in renderWords; this change does not alter activeHalt or lifecycle behavior.

The new HOME vector is (-0.8, 0, -1.4); both initial framing and unfollow use it. The supplied 1440 by 900 measurements put the highest chip at 211 px and the HUD bottom at 135 px, a 76 px band. This is evidence for those states, not phone containment. AUDIT-CDH-0016 F3's phone qualification still applies. The wide calm capture and manifest show six 403 px columns at 2560 by 1080, consistent with the 2488 px inner width and five 14 px gaps. F2 records the narrow-width consequence the supplied wide capture cannot test.

**Images and provenance.** All five supplied PNGs below were opened as image input. They are Cowork's Chromium 1194/SwiftShader VM captures, not native canvas exports or new Codex captures. All 14 file hashes in the CDH-0017 delivery table match: eight historical document files and six evidence files. The manifest's first two paths retain earlier bubble names; its delivered table supplies the matching below-at-refusal and below-at-note filenames. The committed body hash independently matches `54e07dbd8e385927b397e5df8afbd7f6226f226ca4c1fbb5c77ea6423132e92e`. The local wrapper and local three.js package are not present here. The station is unverified standalone in this run; no network fetch or native interaction was attempted.

| Evidence under logs/scratch/design-review/cdh-0017/ | SHA-256 |
| --- | --- |
| `standalone-deck-bubbles-below-at-refusal-1440x900.png` | `15029e9e90db9b5e96eb65365148589d9893b3c5da2465bd569d0dad2c65bf6a` |
| `standalone-deck-bubbles-below-at-note-1440x900.png` | `9eff0adf47935e1c69ad7b0af1b8df4607a1f99662cb0bb2abffd104a9e8b475` |
| `standalone-deck-halt-key-1440x900.png` | `b3db9c2d60f433c8d094b660c56bdc2879c4c5fd6669b6d1e5bbf7bcb39c9f3a` |
| `standalone-calm-halt-key-1440x900.png` | `b9ec162872d89d2b3a1c2bc0604e3c95c9687f475fe254fbc545bf40f471f0fe` |
| `standalone-calm-wall-2560x1080.png` | `38e66ebb96d19bfaef4c53a800618b53eb37e74a3fbb123a56273970b5b3b00f` |
| `manifest.json` | `169385641de9d50427ac3e6c7f8372201783306cc21c38a6ffd02e7b79b56f11` |

Independent results are under logs/scratch/design-review/cdh-0018/: checks.json SHA-256 `ab0e82edbb90c27bcb3b37bbafcc40b8e5097daf6f6993be94e4916d68ce163d`; source-manifest.json SHA-256 `c36da7bfb451557572b175fed2bb8487d0a648d92bac993c065a401f4082cdf7`. Grid figures are calculations from CSS, not browser box measurements.

**Scores and taste.** Every judgement item in the reviewed open list has a stakes-times-edge score: three asked items at 2.8, 2.4 and 2.4, each with a recommendation, and 14 decided items from 0.2 through 1.2. Three checks and three facts are correctly distinguished from judgement. The CW17 disposition needs correction in the next build because F1 disproves complete closure. No Michou answer has been inferred; the asked-and-answered line and tally remain untouched.

F1 is a check. F2's cap is 2 × 0.1 = 0.2: build in the next cycle while preserving the desktop preference. Accepting the recorded CW25 pixel touch pending native observation is 1 × 0.2 = 0.2; no geometry patch is justified by a nonpersistent edge touch. The first three taste priorities remain the existing HUD separation (1.0), bubble separation (0.6), and calm-grid width (0.6). CDH-0017 implements all three; retain them, with F2's narrow-width correction. The existing brief remains: keep the station direction, let station join the wall, and retain the chalk silhouette without a personal likeness. These are recommendations, not approvals.

Report validation: `uv run --no-sync kgme lint --root docs/audit/cockpit-design` returned 18 notes, 0 blocking, 16 advisory and 1 cosmetic; this report has only the expected reviewed_sha advisory.
