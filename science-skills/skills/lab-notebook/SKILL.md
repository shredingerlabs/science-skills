---
name: lab-notebook
description: Keep an append-only research log of every analysis run, first look at outcome data, dead end, decision and deviation, tied to code version and data checksum. Use throughout any analysis or literature work - after each run, surprise, decision, search, or at session end - and when resuming or handing over a project.
license: MIT
---

# Lab Notebook

The report shows the path that worked. The log shows the whole path, and the difference between the two is where hidden bias lives. It is also the only honest source for the **number of analyses tried** (multiplicity) and for **when outcome data was first looked at** (what `preregister` can claim).

The log is `docs/science/LOG.md` by default, under the docs dir configured in `docs/science/CONFIG.md`. If it is missing, run `<setup-science-skills>/scripts/scaffold.sh`, or create it with the header below.

## Rules

- **Append only.** Never edit or delete an earlier entry. To correct one, add a new entry that points back to it and says what was wrong.
- **Write as work happens**, not reconstructed afterwards from memory.
- **Log every analysis run**, reported or not, and every dead end: a model that did not converge, a null, a search that found nothing, an idea dropped and why.
- **Log first looks.** The first time outcome data is examined, how, and by whom. If that happens before the freeze, the analysis is exploratory (`preregister`).
- **Log deviations** here as well as in `docs/science/deviations/` (`run-analysis`).
- **Log decisions with reasons**, not only results.
- **Reference, do not paste.** Point to files under the outputs dir; include the git short hash and the data checksum so the entry ties to exact code and data.
- **Redact secrets and personal data** before writing anything.

## Entry format

```
## YYYY-MM-DD HH:MM  <short title>
Why:      what question or doubt prompted this
Did:      command or action; git short hash; data checksum if relevant
Result:   what came out, including negative or confusing results (path for anything large)
Decision: what was decided and why
Next:     what follows
```

Several lines are enough. Write one after every analysis run, surprising output, change of direction, search, passed or failed check, and at the end of a session ("where things stand").

## Resuming or handing over

Read the log **first**; it is the handoff. Summarise from it what is done, what is open and what not to retry. Do not rely on memory of earlier turns.

## Header for a new log

```markdown
# Lab notebook
Append only. Newest at the bottom. Correct old entries with a new entry that points back.
---
```
