---
name: research-retro
description: Look back over a research session or project and turn what went wrong into deterministic checks and written project rules, not good intentions. Use after finishing or abandoning an analysis, after a failed review, or when an error was found late.
license: MIT
---

# Research Retro

After a piece of work, especially one where something was found late, ask what in the **environment** allowed the problem, then change the environment so the next project cannot repeat it silently. This skill does not redo the science.

Run it in the session being reviewed, before clearing. After clearing, point it at `docs/science/LOG.md`, `docs/science/reviews/`, `docs/science/deviations/` and the git history.

## 1. Gather incidents

Read the log (dead ends, surprises), the deviation files, review findings and responses, any `contradicted` or `not found` source-ledger rows, failed checks, and `git log` for reverts and "fix" commits. List concrete incidents: what went wrong, when it was caught, by what, and how late.

## 2. Find the cause in the environment

For each incident ask:

- Could a **script** have caught it? (unit test, row-count assertion, schema check, manifest hash check, a lint for absolute paths)
- Could a **rule** have prevented it? (a line in the preregistration template, a convention in `AGENTS.md`)
- Was information **missing**? (unit unknown, provenance unasked, no data dictionary)
- Was **review** the gap? (wrong axis, too late, shared blind spot)

## 3. Propose changes, by kind

- **Mechanical mistakes → deterministic checks.** Name the exact check, where it lives (a `checks/` script, the pipeline entry point, CI), and how it fails loudly.
- **Judgement mistakes → written rules.** Give the exact wording and where it goes.
- **Missing information → a recorded fact** in the data note or source ledger.
- **Process gaps** (for example "the plan was written after the outcome was seen") are reported plainly, with advice for next time. Do not hide them.

Also record what worked, so it is kept.

## 4. Confirm, then write

Show the user the proposed changes as a short list, each with the incident behind it. Apply only what they accept. Never edit a frozen preregistration or an earlier log entry. Write `docs/science/retro/YYYY-MM-DD.md` (incidents, causes, changes made) and append a `lab-notebook` entry.

If one of these skills was wrong or unclear in this project, say which and why, so the skill can be fixed.
