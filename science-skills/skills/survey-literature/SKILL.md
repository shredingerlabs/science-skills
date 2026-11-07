---
name: survey-literature
description: Ground a research question in prior work - standard methods, known confounds, prior effect sizes - using a documented, repeatable search of primary sources. Use after the question is framed and before designing the analysis, or when the user asks what is known about a topic.
license: MIT
---

# Survey Literature

Establish what is already known, so the analysis uses standard methods, expects a realistic effect size, and controls known confounds. A survey you cannot repeat is an anecdote.

Prerequisite: an approved question in `docs/science/questions/`. If none exists, run `/grill-hypothesis` first.

## Rules

1. **Primary sources over summaries.** Papers, registries, datasets, standards, and official documents, not blog posts, press releases or AI-generated overviews. A secondary source is a pointer to a primary one, never the evidence itself.
2. **Log every search.** In `docs/science/surveys/<slug>-searchlog.md` record: date, database/tool, exact query string, filters, result count, what was screened in or out and why. Another person must be able to rerun it.
3. **Search for the disconfirming evidence.** Run at least one query designed to find disconfirming or null results ("no effect", "failed replication", "retraction", "negative"). Report what you find.
4. **Nothing from memory.** A reference you "remember" is a hypothesis about a reference. Every source used goes through `source-verification` before it appears in a survey, plan, or report.
5. **Prefer systematic evidence.** Look for meta-analyses, registered reports and pre-registered replications before single studies. Note study design and sample size for each.
6. **Do not search by outcome you hope for.** Query the topic, not the answer.

## What to extract

For each included source, one row in the survey table:

| Source (verified id) | Design | N | Population | Effect (size + CI) | Known confounds / caveats | Status in ledger |
|---|---|---|---|---|---|---|

Then answer, in the survey file:

- **Standard methods:** how is this question normally analysed, and why?
- **Expected effect size** (with source) for a power calculation. If none exists, say so; do not invent one.
- **Known confounds and measurement problems**
- **Where the field disagrees**, and which side the evidence favours
- **Gaps:** what has not been studied
- **Search limits:** databases not covered, languages, date range, paywalls

## Done when

Every included source has a row in the source ledger, and the survey file answers the six questions above.

## Output

`docs/science/surveys/YYYY-MM-DD-<slug>.md` plus the search log. Hand off to `data-intake` or the analysis design.
