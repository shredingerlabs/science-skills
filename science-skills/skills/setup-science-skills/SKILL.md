---
name: setup-science-skills
description: Configure this skill pack for a repo - where research docs live, language and environment manager, raw data location, review policy. Run once per repo before the other science skills.
license: MIT
---

# Setup Science Skills

Run once per repo. The other skills read `docs/science/CONFIG.md` and fail loudly if it is missing.

## Process

1. Inspect the repo first: language files (`pyproject.toml`, `renv.lock`, `environment.yml`, `*.Rproj`), existing `data/`, `docs/`, git status. Do not ask what you can see.
2. Ask only what you could not infer, as one round of numbered questions with your recommended answer for each:
   - **Docs location** (default `docs/science/`)
   - **Raw data directory** (default `data/raw/`). It will be treated as read-only.
   - **Outputs directory** (default `results/`). `preregister` audits that nothing lands here before the freeze.
   - **Language and environment manager** (default: Python + `uv`; or R + `renv`; or conda-lock)
   - **Git available?** The freeze audit needs it. If no, say so: pre-registration then relies on an external timestamp (OSF, a signed tag pushed to a remote).
   - **Stakes** (`exploratory` / `internal decision` / `publication` / `clinical or safety-relevant`). Higher stakes tighten the review: see `red-team`.
   - **Reviewer model.** Which model or agent runs `/red-team`? Strongly prefer a different model from the one doing the analysis.
3. Run `scripts/scaffold.sh <docs-dir> <raw-dir> <outputs-dir>` to create the layout.
4. Write `docs/science/CONFIG.md` with the answers (template below).
5. Offer to append `docs/AGENTS-snippet.md` from this pack to the repo's `AGENTS.md`, so the laws apply even when a skill does not auto-trigger. Show the diff, do not apply silently.
6. Offer to copy `agents/science-reviewer.md` to `.opencode/agents/` (read-only reviewer subagent used by `/red-team`) and `commands/*.md` to `.opencode/commands/` (the slash entry points such as `/red-team`). `install.sh` does both.

## CONFIG.md template

```markdown
# Science config

- docs_dir: docs/science
- raw_data_dir: data/raw          # read-only; never edited, only added to
- outputs_dir: results
- language: python
- env_manager: uv
- git: yes
- stakes: publication
- reviewer: <model or agent name>, different from analyst: yes/no
- reporting_guideline: <CONSORT | STROBE | PRISMA | TRIPOD | ARRIVE | none>
```

## Layout created

```
docs/science/
  CONFIG.md
  questions/        one file per question (grill-hypothesis)
  surveys/          literature surveys + search logs (survey-literature)
  sources/          source ledger (source-verification)
  LOG.md            append-only lab notebook (lab-notebook)
  data/             data manifests + dictionaries (data-intake)
  validation/       positive/negative-control evidence (validate-pipeline)
  preregistrations/ frozen plans (preregister)
  deviations/       anything that departed from the plan (run-analysis)
  reviews/          independent review findings + responses (red-team)
  reports/          claim ledgers + reports (report-findings)
  retro/            lessons turned into checks and rules (research-retro)
```
