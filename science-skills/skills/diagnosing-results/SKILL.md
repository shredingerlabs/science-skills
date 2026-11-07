---
name: diagnosing-results
description: Disciplined root-cause loop for surprising, implausible, too-good, or failed analysis results - suspect the pipeline before the science, never drop inconvenient data silently. Use when a result looks wrong, contradicts the literature, flips under a small change, or a validation check fails.
license: MIT
---

# Diagnosing Results

A discipline for results that do not look right. Surprises are information; the failure mode is making them disappear. **The anomaly is the finding until it is explained.**

Mirrors a debugging loop, because most anomalous results are bugs, and the rest are discoveries you only get to keep if you can rule out the bugs.

## Phase 0: Freeze the state

Stop changing things. Record the exact command, commit, seed, data manifest hash and the anomalous output, before touching anything. If you cannot reproduce the anomaly twice, that is the first finding (nondeterminism: see `reproducible-compute`).

## Phase 1: Build a loop that reproduces it

Get one command that shows the anomaly in seconds, on the smallest input that still shows it. Minimise: cut rows, columns, steps one at a time, rerunning after each cut, keeping only what is load-bearing. You do not understand an anomaly you cannot reproduce on demand.

## Phase 2: Rank hypotheses, falsifiably

Write **3-5** candidate explanations before testing any. Each must state its prediction: "If X is the cause, then doing Y will make the anomaly vanish / worsen." A hypothesis without a prediction is a vibe: sharpen or discard it. Order of suspicion, most likely first:

1. **Data**: wrong file/version, units, encoding, missing-value codes read as numbers, duplicated rows, a join that fanned out or dropped rows, timezone shift, mislabelled groups, **leakage** (the outcome, or a proxy for it, is in the features)
2. **Code**: off-by-one, wrong axis, wrong key, silent type coercion, stale cached intermediate, a transform applied twice or not at all, a global RNG consumed in a different order
3. **Method**: assumption violated, wrong test for the design, non-independent units, collinearity, a model that did not converge, a metric that does not measure what you think
4. **Environment**: library version change, thread count, platform, locale
5. **The world**: the effect is real, or the literature was wrong, or the population differs

"Too good to be true" almost always sits in 1 or 2 (leakage, duplicate entities across splits, an outcome-derived column). "Contradicts the literature" is usually 1, 3 or population mismatch. Check them in that order.

Show the ranked list to the user before testing if they are present. They often know what changed.

## Phase 3: Test one variable at a time

Each probe maps to one hypothesis's prediction. Prefer a controlled experiment to inspection: swap the file version, shuffle the labels, simulate data with a known answer through the same pipeline (`validate-pipeline`), run the old code on the new data and vice versa, bisect over commits. Never "print everything and look".

## Phase 4: Resolve - without deleting evidence

- **Cause found and it is a defect** (bug, data error): fix it, add a test that would have caught it, rerun **all** downstream steps. If the plan was already frozen, record a deviation (`run-analysis`); the affected analysis's status depends on whether the fix was independent of the outcome.
- **Cause found and it is a real feature of the data** (e.g. a site with a distinct population): report it. A subgroup you discovered after looking is exploratory.
- **Cause not found**: say so. List what was ruled out and how. Keep the anomalous data in. Report the result with the unexplained anomaly flagged.

**Hard rules**

- Never exclude data because it is inconvenient. Exclusions need a rule that does not depend on the outcome, and an entry in the deviation log.
- Never rerun with a different seed, split or threshold "to see if it goes away" and report only the run that looks right.
- Never alter the analysis and keep the old confirmatory label.
- A fix for a bug found *because* the result was disappointing deserves extra scrutiny: also hunt for bugs that would flatter the result.

## Phase 5: Close out

- The anomalous result, the explanation (or its absence), the evidence, and the fix go in `docs/science/reviews/anomaly-<slug>.md`.
- A regression test or validation check now exists for it.
- Any claim that depended on the affected result is re-verified.
