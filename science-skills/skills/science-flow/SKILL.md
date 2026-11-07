---
name: science-flow
description: Ask which scientific-workflow skill fits your situation. A router over the skills in this pack. Use when starting any research, data analysis, or claim-making task and unsure where to begin.
license: MIT
---

# Science Flow

A router. Find where the user is in the research lifecycle, name the skill that fits, and stop. Do not do the work of the skill yourself.

## The five laws

Every skill in this pack enforces one or more of these. If a request would break one, say which and stop.

1. **No data before a question.** No outcome data is loaded, plotted or modelled until a falsifiable question is agreed (`/grill-hypothesis`).
2. **No confirmatory claim without a frozen prediction.** Predictions are committed before outcomes are seen (`preregister`). Everything else is exploratory, and labelled so.
3. **No claim without a verified source or a reproduced result.** Citations are opened and read; numbers are re-computed from a clean run (`source-verification`, `reproducible-compute`).
4. **No inconvenient data dropped silently.** Anomalies are diagnosed, not deleted (`diagnosing-results`).
5. **No self-grading.** Anything reported is attacked by a reviewer who did not produce it (`/red-team`).

## The flow

```
/setup-science-skills        once per repo
        │
/grill-hypothesis            falsifiable question, no data touched
        │
survey-literature            what is already known; every source verified
   └─ source-verification
        │
data-intake                  raw data immutable, checksummed, profiled blind to outcome
        │
validate-pipeline            prove the pipeline can detect a known effect and a null
        │
preregister                  freeze predictions, analysis, decision rules  ← Iron Law
        │
/run-analysis                execute exactly what was frozen, in a pinned environment
   ├─ reproducible-compute
   ├─ statistical-discipline
   └─ diagnosing-results     when a result looks wrong
        │
/red-team                    independent review, clean-room re-run
        │
/report-findings             claim ledger, verification gate, archive
        │
/research-retro              turn mistakes into checks and rules

(lab-notebook runs underneath every stage: append-only log of all runs, first looks, decisions)
```

## Which skill, when

| Situation | Skill |
|---|---|
| First time in this repo | `/setup-science-skills` |
| "I want to see if X affects Y", fuzzy idea, a dataset and a vague question | `/grill-hypothesis` |
| "What is known about this?", "find sources", "is this citation real?" | `survey-literature`, `source-verification` |
| A new dataset arrives | `data-intake` |
| "Will this pipeline find anything at all?" | `validate-pipeline` |
| About to run a test, fit a model, or compute a p-value | `preregister` first |
| Plan is frozen, time to run | `/run-analysis` |
| Result is surprising, too good, or wrong-looking | `diagnosing-results` |
| "Is this ready?", "check my analysis", a reviewer comment arrived | `/red-team` |
| Writing up, summarising, about to say "we found" | `/report-findings` |
| Anything was tried, looked at, or decided | `lab-notebook` (always on, append-only) |
| Project finished, abandoned, or an error was found late | `/research-retro` |

## Rules for this skill

- Ask at most one question: which stage the user is at, if it is not obvious from the repo (`docs/science/`).
- Check `docs/science/` for existing question, prereg and report files before recommending a stage. Never send the user back to a stage they have already completed.
- If the user asks to skip a stage, state what claim status that costs them (usually: "this becomes exploratory") and let them decide.
