# Provenance and vetting

What this pack was built from, what was checked, and what was not. Checked 27 Oct 2026.

## Design references (read, cloned and inspected)

| Source | Licence | What was taken | Evidence of quality |
|---|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | The *shape*: small composable skills, a one-time setup skill, "grilling" as the alignment step, a debugging loop built around a tight feedback signal, two-axis review by parallel sub-agents, slash entry points. Prose here is original. | Widely used; not independently benchmarked. |
| [K-Dense-AI/science-superpowers](https://github.com/K-Dense-AI/science-superpowers) | MIT | The framing "pre-registration is to science what TDD is to software", the freeze/audit idea, and the red-team axes. Implementation here is independent and adds executable checks. | Documented workflow; skill behaviour not independently evaluated. |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | MIT | Not copied. Recommended as the **domain companion** (statistics, power, experimental design, peer review, literature, 170+ package skills). | Has CI: skill-spec validation, a security scan of skills, per-skill tests under `tests/`, `last-reviewed` dates. This is the strongest "tested" signal found. |
| [OpenCode docs: skills, agents, commands](https://opencode.ai/docs/skills) | n/a | Exact SKILL.md rules (name regex, 1-1024 char description, directory = name), `.opencode/{skills,agents,commands}` locations, agent `permission` keys. `tools/validate.py` enforces them. | Primary documentation. |

## Seen but not used

- **imbad0202/academic-research-skills**: well-built suite with evals and citation-integrity checks, but licensed CC BY-NC 4.0, so it cannot be bundled or adapted here. Worth installing separately for non-commercial paper-writing work.
- Curation indexes ([awesome-academic-skills](https://github.com/O0000-code/awesome-academic-skills), [skillselion guide](https://skillselion.com/guides/best-academic-research-skills-for-claude-code)) were used to find candidates. Their popularity numbers are inconsistent within the pages themselves and measure installs, not correctness. Several listed skills have no licence, unscoped shell permissions, or a hard-coded credential; none of those were used.

## What "tested" means here

- `tests/test_scripts.py` (24 tests, stdlib only): freeze/audit logic in a real temporary git repo (including tamper detection), manifest round trip and verification, DOI extraction and retraction flagging, scaffold idempotence, installer, and the validator itself.
- `tools/validate.py` enforces OpenCode's SKILL.md rules, script and command references, and agent permission keys.
- **Not tested:** live Crossref lookups (the build sandbox could not reach the API; the code path is exercised with mocks and failure injection, and an unreachable network reports `UNCHECKED`, never a pass). **Not evaluated:** whether an LLM agent actually follows each skill under pressure. Run a few real tasks and use `research-retro` to find where a skill is ignored.
