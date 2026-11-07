# science-skills

Agent skills (OpenCode, also readable by Claude Code) that put a scientific method around a coding agent: **question → sources → plan frozen in advance → reproducible computation → independent review → claim-backed report**. The structure follows [Matt Pocock's skills](https://github.com/mattpocock/skills): small, composable skills, a one-time setup, an interview step, and a debugging loop. The central discipline is pre-registration instead of test-driven development. Provenance and vetting notes: [docs/SOURCES.md](docs/SOURCES.md).

## The flow

```
/setup-science-skills   once per repo
/grill-hypothesis       vague idea -> falsifiable question (no outcome data touched)
survey-literature       logged, repeatable search of primary sources
  source-verification   every citation opened; ledger of claim-source pairs; DOI/retraction check
data-intake             raw data immutable + checksummed; blind profiling; leakage review
validate-pipeline       can the pipeline find a known effect and stay quiet on noise?
preregister             freeze predictions + analysis + decision rules (git-audited)
/run-analysis           execute exactly what was frozen, pinned and seeded
  reproducible-compute  lockfile, seeds, provenance, clean-room rerun
  statistical-discipline
  diagnosing-results    when a result looks wrong: suspect the pipeline, never drop data silently
/red-team               fresh, read-only reviewers: protocol / rigor / claims
/report-findings        claim ledger, gate, confirmatory vs exploratory, archive
/research-retro         turn mistakes into checks and rules
lab-notebook            append-only log under every stage
science-flow            "where am I, what next?" router
```

| Matt Pocock skill           | Science counterpart                     |
| --------------------------- | --------------------------------------- |
| grill-me                    | grill-hypothesis                        |
| tdd                         | preregister + validate-pipeline         |
| diagnosing-bugs             | diagnosing-results                      |
| research                    | survey-literature + source-verification |
| code-review (parallel axes) | red-team (protocol / rigor / claims)    |
| setup-matt-pocock-skills    | setup-science-skills                    |
| retro                       | research-retro                          |

## Install

```bash
./install.sh            # into ./.opencode/{skills,agents,commands}
./install.sh --global   # into ~/.config/opencode/...
./install.sh --claude   # skills only, ~/.claude/skills
./install.sh --link     # symlink instead of copy; --dry-run to preview
```

Then, in your project, run `/setup-science-skills`. It writes a config, scaffolds `docs/science/`, and offers to append [docs/AGENTS-snippet.md](docs/AGENTS-snippet.md) to `AGENTS.md`.

OpenCode skills are loaded by the model from their descriptions; the slash commands in `commands/` are thin wrappers that load a skill by name. `agents/science-reviewer.md` is a read-only subagent (can write only to `docs/science/reviews/`) used by `/red-team`.

## What it does not do

It does not certify truth. Review by an agent shares the author model's blind spots (use a different model for the reviewer where you can), and high-stakes, clinical or human-subject work still needs a domain expert, a statistician and ethics review. For domain methods (power, DOE, specific statistical packages, peer-review checklists) pair this with [K-Dense scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills).

## Develop

```bash
python3 tools/validate.py                      # OpenCode SKILL.md rules, references, agent keys
python3 -m unittest discover -s tests          # script tests, stdlib only
```

MIT licensed.



## Inspired by:

- [mattpocock/skills](https://github.com/mattpocock/skills)
- [K-Dense science-superpowers](https://github.com/K-Dense-AI/science-superpowers)
- [K-Dense scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
- [awesome-academic-skills](https://github.com/O0000-code/awesome-academic-skills)
- [skillselion academic skills guide](https://skillselion.com/guides/best-academic-research-skills-for-claude-code)
