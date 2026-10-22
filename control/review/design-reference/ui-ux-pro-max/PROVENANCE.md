# ui-ux-pro-max — vendored review rubric (text only)

Source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill, MIT (the `LICENSE` beside this file is the repository's, verbatim).
Pinned to commit `56ea9cf174ed86786187daa9de0e6247cb0747e4` (2026-10-15T09:04:34+07:00, "feat(copilot): install as an Agent Skill in .github/skills (#533)").
Reviewed by the substantive Cowork session on 2026-10-15; vendored by the design session on 2026-10-15 (Michou's relay, 22:43). Toolbox row (ADR-020) follows HANDOFF-0044.

Use: a **review rubric only**, cited from `tools/review/design-prompt.md`. Never its generator: its `--design-system` output proposes a landing-page pattern, a slate/green palette and a Google-Fonts face; the cockpit's palette and type are decided, and AUDIT-CDH-0011 S6 removed remote fonts. Not vendored: the plugin, the CLI, the other skills, `references/pro-rules.md` (native/mobile by its own scope notice).

| File here | Path in the repository at the pinned commit | SHA-256 | Bytes |
|---|---|---|---|
| `references/quick-reference.md` | `.claude/skills/ui-ux-pro-max/references/quick-reference.md` | `0609bc7c89dacb40472465d8fc14257b56b2c43439660fc8d6fa3b8c022e1876` | 24,526 |
| `data/ux-guidelines.csv` | `.claude/skills/ui-ux-pro-max/data/ux-guidelines.csv` | `ff81ec613f70ba9fc3fcce52dbe4ae35d44b2079dbe6dc066d2d6e38c28facd5` | 27,516 |
| `data/stacks/threejs.csv` | `.claude/skills/ui-ux-pro-max/data/stacks/threejs.csv` | `155d583b9c64da0df4b6c6cb060c02eab222505e0734d6353da02c9e2b5d982b` | 46,769 |
| `LICENSE` | `LICENSE` | `738f69dfa83db5c347c678fb9d90e560877059f0de93a327c39001bff92dc014` | 1,075 |

The same three files also exist in that commit under `src/ui-ux-pro-max/` and `cli/assets/` (the CSVs byte-identical; `quick-reference.md` there is a longer template variant, `0a6da6ef…`, not taken).

How to cite: a finding may name a rule id from `quick-reference.md` (for example `focus-not-obscured`, `web-target-size`, `auto-rotation-controls`) and the `No` of the matching row in `ux-guidelines.csv` (100, 104, 108; the live-badge rule is 118) or in `stacks/threejs.csv` (1–9 are the setup rows: pinned package, geometry, addons, drag fallback, ESM imports, one renderer, pixel-ratio cap at 2, alpha canvas, aspect on resize). The finding keeps its ADR-016 class; the rubric's own severities (Critical/High/Medium/Low) are advisory. One rule the rubric lacks is added in `design-prompt.md`: WCAG 2.1.4 character-key shortcuts.
