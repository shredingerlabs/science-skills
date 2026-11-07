---
name: report-findings
description: Turn reviewed results into a report via a claim ledger, a verification gate, honest confirmatory-versus-exploratory labelling, and a complete archive. Use when writing up, summarising, or about to say "we found", "the data show", or "this proves".
license: MIT
---

# Report Findings

Evidence before claims, every time. A report is a set of claims, each of which must be traceable to evidence you re-checked today.

## Gate (check, do not assume)

- [ ] `prereg.py audit` passes for every confirmatory result
- [ ] `/red-team` has run; no **fatal** or **major** finding is open
- [ ] Clean-room rerun matched (`reproducible-compute`)
- [ ] Source ledger has no row that the claim as worded cannot support (`source-verification`)

Any box unchecked → stop and say which. "I ran it earlier" is not a check; run it again and show the output.

## 1. Build the claim ledger first

`docs/science/reports/claim-ledger.md`, **before** drafting prose:

| # | Claim (exact wording to be used) | Type | Evidence (file, commit, run id) | Verified how, when | Effect + interval | Status | Caveats |
|---|---|---|---|---|---|---|---|

- **Type**: `confirmatory` (pre-registered test) | `exploratory` | `descriptive` | `literature` (cites a ledger source)
- **Verified how**: the command you re-ran or the source row you re-opened, and its date. If you cannot fill this column, the claim does not go in the report.
- **Status**: `supported` | `weakened` (wording narrowed) | `withdrawn`

The report may contain only claims in the ledger, worded as in the ledger.

## 2. Wording discipline

- Match verbs to design: randomised experiment → "caused/reduced"; observational → "was associated with", "predicted".
- State effect sizes with intervals and n. Never "significant" alone.
- Report **everything the plan specified**, including the nulls, the failed robustness checks, and the deviations. Silence about a null is a claim.
- Separate sections: **Confirmatory results** | **Exploratory results (hypothesis-generating; not tested)** | **Deviations from the plan** | **Limitations**.
- Say what the study cannot tell us, and the strongest alternative explanations that remain.
- Do not invent a narrative: if the result is a null or inconclusive, the report is a null or inconclusive report.
- Pick a reporting guideline if one applies (CONSORT trials, STROBE observational, PRISMA reviews, TRIPOD prediction models, ARRIVE animal studies) and follow its checklist. Use the one named in `CONFIG.md`; if none, ask.

## 3. Report structure

```
Title - plain statement of the question
Summary - what was asked, what was found (incl. nulls), how sure we are, in plain language
Question and preregistration - link to the frozen plan, freeze commit, and audit result
Data - provenance, manifest hash, exclusions and why
Methods - exactly the plan; software and versions; seed
Confirmatory results
Exploratory results
Deviations
Review - what the independent review found and how each finding was resolved
Limitations - including review limits (see red-team)
Reproduction - how to rerun; clean-room result
References - verified ledger sources only
```

## 4. Decide with the user

What follows from this result? **Publish / preprint** | **iterate** (new preregistration on new data) | **shelve** | **replicate first** | **discard**. A null result is a result; offer to write it up (registered report, preprint, or internal note) rather than let it vanish.

## 5. Archive

Complete `reproducible-compute`'s archive list, plus the claim ledger and the finished report. Then offer to tag the commit and prepare a deposit (Zenodo, OSF) with a DOI.

## 6. Final check

Re-read the finished report against the ledger line by line. Every number traces to a run; every citation to a `verified` row; every confirmatory claim to an audited plan. Then, and only then, say the work is done.
