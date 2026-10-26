---
id: TOOLBOX
type: note
status: active
created: 2026-10-25T23:40:00-07:00
modified: 2026-10-25T23:40:00-07:00
author: claude-code
source: inferred
sources: ["ADR-020", "HANDOFF-0044", "uv.lock", "pyproject.toml", "kgme.toml", "tests/station_equivalence.py", "docs/design/cockpit-v0/station/README.md"]
tier: 2
---

# The toolbox (ADR-020)

Every third-party thing KGME uses has one row here: a package, a JavaScript module, a vendored skill, a harness, a model, an API, an asset pack. Adding a row is how a tool comes in; deleting the row and what it points at is how it goes. `kgme lint` keeps the rows and the tree in step (`kgme/toolbox.py`):

- every import outside the standard library in `kgme/` and `cockpit/` names a package row;
- no `<script src>` in `cockpit/` names a host;
- every file under `cockpit/static/vendor/` and every vendored skill under `skills/` has a row whose sha256 is what the tree holds.

**What the columns mean.**
- **held:** what the sha stands behind.
  - A repository path is verified by `kgme lint` on every run. A folder (a skill) is hashed as the sorted `<path> <sha256>` lines of its files.
  - `uv.lock`: the lock holds the hashes.
  - `pending: <path> (HANDOFF-NNNN)`: the file that handoff will vendor. The sha is of the file as it will be held.
  - `machine: <path>`: a harness or model as installed on this machine. Recorded, not verifiable from a clone.
- **name:** a package row names its import as `(import <module>)`.
- **egress:** the host a row needs. A model or an API must name one.
- **Transitive packages** (colorama, iniconfig, packaging, pluggy, pygments) come with pytest through `uv.lock`, and its hashes are theirs.

| name | kind | for | source | licence | version | held | sha256 | egress | used in | handoff |
|---|---|---|---|---|---|---|---|---|---|---|
| pyyaml (import yaml) | package | front matter parsing | https://pypi.org/project/PyYAML/ | MIT | 6.0.3 | uv.lock | uv.lock | none | kgme/frontmatter.py | HANDOFF-0025 |
| ruff | package | lint and format in make check (dev) | https://pypi.org/project/ruff/ | MIT | 0.16.7 | uv.lock | uv.lock | none | Makefile | HANDOFF-0025 |
| pytest | package | the test suite (dev) | https://pypi.org/project/pytest/ | MIT | 9.1.1 | uv.lock | uv.lock | none | tests/ | HANDOFF-0025 |
| three.js three.module.js | module | the station's renderer, unminified | https://cdn.jsdelivr.net/npm/three@0.182.0/build/three.module.js | MIT | 0.182.0 | pending: cockpit/static/vendor/three-0.182.0/three.module.js (HANDOFF-0058) | d835eab0b3bca3fdfd51e2ce7d06911f4a089b08db73cc3cd70fe5e3005a623f | none | docs/design/cockpit-v0/station/ (from the CDN, on the canvas only) | HANDOFF-0044 |
| three.js three.core.js | module | imported by three.module.js | https://cdn.jsdelivr.net/npm/three@0.182.0/build/three.core.js | MIT | 0.182.0 | pending: cockpit/static/vendor/three-0.182.0/three.core.js (HANDOFF-0058) | 283be43b2229e15f46dac84cd19354ede5f06cac7ffb185e765cfcfb2c1eec90 | none | docs/design/cockpit-v0/station/ (from the CDN, on the canvas only) | HANDOFF-0044 |
| grilling | skill | interview the user about a plan, question by question | https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/productivity/grilling | MIT | 49dd158d (SKILL.md befdff1e27a1dfe2…, 2,049 B) | skills/grilling/ | da5b52cf1fec64d090eb679138468f9c3d86980827d55d6dc34550553f4198bf | none | .claude/skills/grilling, .agents/skills/grilling | HANDOFF-0044 |
| retro | skill | a retrospective on an agent session | https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/retro | MIT | 49dd158d (SKILL.md 33fbc28568e3146f…, 4,369 B) | skills/retro/ | b6517d5dce806a5d1ed35d5f990df1da0591224a62f2cabe909fdc7db3bfc8d6 | none | .claude/skills/retro, .agents/skills/retro | HANDOFF-0044 |
| diagnosing-bugs | skill | a red-capable loop before a fix | https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/diagnosing-bugs | MIT | 49dd158d (SKILL.md 849198df88cdb65f…, 8,664 B) | skills/diagnosing-bugs/ | 466351ff8751e40ba310f5e7033320cff730090d1883d39b810f3cde281360f0 | none | .claude/skills/diagnosing-bugs, .agents/skills/diagnosing-bugs | HANDOFF-0044 |
| pr | skill | a pull request description; CREDITS.md names Dex Horthy's show-me | https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/pr | MIT | 49dd158d (SKILL.md ab63f1cf78647389…, 4,169 B) | skills/pr/ | f7f257d59f262cc8fd66b5c2ecfa6c07703d06edf6cf12e6ec7365802353e1b9 | none | .claude/skills/pr, .agents/skills/pr | HANDOFF-0044 |
| Node | harness | runs tests/station_equivalence.py; Codex CLI and Claude Code run on it | https://nodejs.org/ (through nvm) | MIT | v25.9.0 | machine: ~/.nvm/versions/node/v25.9.0/bin/node | 4b3fe8b384e30ee917e28a9f5b79a3ca64b72b13b70d9ab2273e6e9a823f4cbf | none | tests/station_equivalence.py | HANDOFF-0037 |
| Codex CLI | harness | the reviewer (kgme review) and the design track's builder | https://www.npmjs.com/package/@openai/codex | Apache-2.0 | 0.164.0 | machine: ~/.nvm/versions/node/v25.9.0/lib/node_modules/@openai/codex/bin/codex.js | 61b0194f3bb6534439c8d26a3ed57d0805f84b884588b761795323eeb92fcf70 | chatgpt.com:443, api.openai.com:443 | kgme review; control/policy/profiles/codex-reviewer.toml, codex-builder.toml | HANDOFF-0032 |
| Claude Code | harness | the builder's sessions and their hooks | https://www.npmjs.com/package/@anthropic-ai/claude-code | proprietary (Anthropic; the package states SEE LICENSE IN README.md) | 2.1.310 | machine: ~/.nvm/versions/node/v25.9.0/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe | ffb64331bc0ee1b69efb7c2c428bd3ab516bc31b75bf60886b356c97c1c25ffd | api.anthropic.com:443 | kgme session; control/policy/profiles/claude-builder.toml | HANDOFF-0032 |
| Ollama | harness | serves the cheap lane's model on this machine | https://github.com/ollama/ollama (installed as /Applications/Ollama.app, not through Homebrew) | MIT | 0.40.10 | machine: /Applications/Ollama.app/Contents/Resources/ollama | 74e3e350f2e492b4de9b4d45954b35bec344cfe85b7b7cd6a19f4b12ed4f02c2 | localhost:11434 (kgme.toml [providers] ollama_url); Ollama's cloud for cloud models | kgme/cheap.py | HANDOFF-0053 |
| deepseek-v4.1-flash:cloud | model | the cheap lane's model, code only | https://ollama.com/library/deepseek-v4.1-flash | — | cloud tag, Ollama ID e04da138d31e | machine: ~/.ollama/models/manifests/registry.ollama.ai/library/deepseek-v4.1-flash/cloud | 108b307d4de2b1ab965f804cb7f524f10558a0f3504502810278b47704e0ec82 | localhost:11434 (kgme.toml [providers] ollama_url), forwarded by Ollama to its cloud | kgme.toml [models] cheap | HANDOFF-0053 |
| Playwright MCP | harness | browser checks (HANDOFF-0037) and the design fixtures (CDH-0001) | https://github.com/microsoft/playwright-mcp, through the Claude Code plugin playwright (claude-plugins-official) | Apache-2.0 | unpinned: the plugin runs npx @playwright/mcp@latest | machine: ~/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/playwright/.mcp.json | b6fd7e9ccee1682af353854195516826da6970026b68c86ad800ff4d931d3250 | registry.npmjs.org (npx), localhost | logs/scratch browser checks; cockpit design reviews | HANDOFF-0037 |

**Open rows.**
- **deepseek-v4.1-flash:cloud has no licence.** `ollama show --license` returned nothing on 2026-10-25, and no licence is guessed. The row stays advisory until the licence is found.
- **Playwright MCP is unpinned.** Its plugin fetches `@playwright/mcp@latest` on each start. Pinning it means a plugin override naming a version, which is Michou's to decide.
- **Claude Code mods** get a row each when HANDOFF-0059 lands (ADR-024).
- **The data sources** of amendment 3 (FRED, Treasury FiscalData, BLS, the Federal Register, USAspending, Nager.Date, Open-Meteo, SEC EDGAR, Crossref) get a row each when first called.
