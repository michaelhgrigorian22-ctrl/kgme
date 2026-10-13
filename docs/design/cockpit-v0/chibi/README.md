# CDH-0001 illustrated cast

These 7 original editable SVGs implement the approved character direction as a design deliverable. `preview.html` is a synthetic fixture, not a cockpit or live ledger. The implementation report records source hashes, measurements and remaining acceptance gaps. Final visual acceptance belongs to Michou; native canvas verification was done by Cowork under CDH-0004 and CDH-0006.

The source files are `builder.svg`, `reviewer.svg`, `arbiter.svg`, `guard.svg`, `scribe.svg`, `michou.svg` and `stranger.svg`. Each has a transparent 240 × 280 viewBox. `characters.css` provides material mapping, static poses and shared motion. `characters.js` loads these exact local files, clones their SVG geometry and supplies fixture controls. No runtime image atlas, generated replacement support script, external asset, font download or dependency is needed.

The fixture keeps JetBrains Mono first in the font stack and uses system monospace when it is not installed. It does not bundle a font binary or add a font request. The native board retains its existing Google Fonts links. Exact native font rendering was verified under CDH-0004 and CDH-0006; the implementation report distinguishes any standalone fallback observed during measurement.

## Material roles and geometry

There are 6 semantic material roles: `--garment`, `--face`, `--tool` (hat/tool), `--print`, `--dark` and `--accent`. Garment, face and tool each have `-shade` and `-light` cel tones. Each SVG sets its sticker materials inline; shared phosphor CSS deliberately overrides those variables with `!important`. Source fills and strokes use those variables. Fixed ochre cloth is a material, not an amber state signal.

The shared state accent follows text: cyan `#39d0ff` for live/focus, magenta `#ff3d7f` for blocking, amber `#ffb02e` for pending/transient/advisory, green `#4de38a` for ok and muted `#6f8290` for inactive/disconnected treatment. A mode is not a class. In the synthetic fixture, each mode has separately written lifecycle, class and event fields. `—` as a class means the sample has no failure-class value; it does not add a class to the existing vocabulary.

Each `.figure` holds the reusable `.head`, `.body` and `.prop` groups. Head rotation uses `120px 110px`; body motion uses `120px 190px`; the entire figure sags around `120px 245px`. Prop pivots are set inline by the source artist per actor. `.eyes-open` and `.eyes-closed` supply discrete expression swaps. `.effect-fire`, `.effect-halo`, `.effect-melt` and `.chalk` sit apart from the moving figure. Hidden effects default to `display:none` in the SVG; the shared layer enables only the current mode's effect. No animated filters or JavaScript frame-by-frame layout reads are used.

## Actor and mode mapping

| Actor rule, in existing order | Asset | Working motion |
| --- | --- | --- |
| `claude-code.*` | `builder.svg` | The jackhammer moves vertically by 3 source px. |
| `kgme.review` | `reviewer.svg` | The loupe rotates around its hand pivot. |
| `arbiter.*` | `arbiter.svg` | The star staff rocks by 2 degrees. |
| `kgme.guard` | `guard.svg` | The shield lifts by 2 source px and braces. |
| `kgme.*` | `scribe.svg` | The quill rocks through its writing pose. |
| `michou` | `michou.svg` | The flip phone tilts in the hand. |
| `default` | `stranger.svg` | The hand makes a small thinking gesture. |

The fixture repeats this existing mapping; it does not edit `kgme.toml`. Michou is a stylized avatar, not a verified personal likeness.

| Mode | Treatment | Synthetic lifecycle / class |
| --- | --- | --- |
| `idle` | A restrained breath and occasional blink preserve the resting silhouette. | ready / — |
| `working` | Each actor moves its own prop. | active / — |
| `waiting` | A small impatient head turn changes between 2 authored angles. | pending / advisory |
| `transient` | The figure sags while the head and actor identity remain readable. | retrying / transient |
| `blocked` | A small class-colored fire changes shape without full-character flashing. | halted / blocking |
| `done` | A satisfied head pose and slow halo mark the sample's written completion. | completed / ok |
| `asleep` | The actor's authored chalk silhouette is intentionally still. | inactive / — |

Motion interpolates between no more than 2 authored endpoints per animated part. The 49-cell matrix and all run portraits are static. Only the 1 selected detail root can receive `.is-animated`. An `IntersectionObserver`, `visibilitychange` and the actual `prefers-reduced-motion` query remove that class when motion is disallowed. The CSS media query independently enforces reduced motion. Calm hides artwork with `visibility:hidden`, preserving layout and every adjacent fact. No application keyboard commands are attached.

## Display size and palette placement

The full source is displayed in a 72 × 72 CSS-pixel detail box with its aspect ratio preserved. Run portraits use an explicit actor-specific square `data-portrait` crop, displayed at 24 × 24 CSS pixels. The crop deliberately isolates the expressive head. Asleep portraits remain a muted closed-eye head crop; the full detail/matrix pose uses the recognizable chalk outline. Run headers are distinct from the exact 22 px event rows. Context examples retain the original 48 px inactive Phase 2 approval illustration.

Phosphor is the timeline palette. Sticker is allowed only in detail headers and the illustrated Phase 2 model selector. The palette selector controls only the single detail specimen. The static pair comparison is explicitly a detail-header specimen, not a global sticker tweak. Both approved dark surfaces are present for checking transparency. All source art remains decorative and `aria-hidden`; actor, mode, lifecycle, class and event facts are outside it.

## Open the fixture and import the native board

Serve `docs/design/cockpit-v0/` with a local static HTTP server and open `chibi/preview.html`. A local server is needed because the browser loads the sibling SVG files with `fetch`; a `file:` URL may be blocked. The fixture itself only requests its 7 same-origin SVGs plus the sibling CSS/JS. It does not require network access beyond the local server.

For a consistent profile scene, open `chibi/preview.html?profile=1`. The selected builder starts in working mode with a 72 px detail; 50 static phosphor run portraits occupy a scrollable sample ledger. The 2 capture buttons record 30 seconds of observed RAF intervals, supported long tasks and sampled input/scroll event-to-next-frame delays. A missing interaction sample means that interaction is unverified. Capture instrumentation runs only while requested; normal operation has no JavaScript animation loop. These measurements do not establish GPU render time or whole-cockpit performance.

Board 10 (`Sprites.dc.html`) renders the cast natively from this same geometry: one hidden `<symbol>` per actor, copied from these files and kept equal to them by `tests/test_design_sprites.py`, with `<use>` specimens, the 49-cell matrix, the palette pairs and the retained context examples as editor markup, and `{{…}}` holes (CDH-0003, CDH-0006). It retains `./support.js`, `<x-dc>`, `<helmet>`, `DCLogic` and the 1440 × 1500 preview metadata. There is no iframe and no load of these files from the board.

Board 11 (`Tray.dc.html`, CDH-0007) carries a second copy of the same 7 symbols and the shared chibi CSS so the active-runs tray can mount as a child component in boards 1, 3, 4, 5, 6 and 9; the drift test holds that copy to these files too.

Native rendering was verified by Cowork under CDH-0004 and CDH-0006 in the private review copy. This fixture stays as the standalone profiling harness; its screenshots are browser evidence, never native proof.

For mechanical verification, `window.chibiFixture.ready` resolves when sources and fixtures are mounted. `select({actor,mode,palette})`, `setCalm(boolean)` and `setProfile(boolean)` drive only the synthetic fixture. `diagnostics()` reports eligibility, active animations, actual visibility/reduced-motion flags and element counts. `profile({duration:30000,calm:false})` returns a capture result; use `calm:true` for its baseline. This API is a design/test convenience, not an application integration surface.
