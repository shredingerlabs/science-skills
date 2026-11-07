---
name: preregister
description: Lock hypotheses, the exact analysis, directional predictions, and decision rules in a frozen, git-timestamped document before any outcome is seen. Use before running any hypothesis test, p-value, model comparison, or effect estimate that will support a claim.
license: MIT
---

# Preregister

The science analogue of writing the failing test first. A prediction is only evidence if it was made before the result.

```
NO CONFIRMATORY CLAIM WITHOUT A FROZEN PREDICTION FIRST
```

If you looked at the outcome before the plan was frozen, that analysis is **exploratory**. You may keep it, report it, and use it to design the next study. You may not relabel it confirmatory. To confirm, preregister and test on data you have not used.

Prerequisites: an approved question (`grill-hypothesis`), a survey (`survey-literature`) or an explicit note that none exists, a data manifest (`data-intake`), and ideally a passing `validate-pipeline`.

## Dry-run before freezing

Before freezing, confirm:

- Every configuration in the plan has run at least once on non-outcome data (simulated, or a held-out validation set), or is known runnable from a measured point.
- The cheapest run that could falsify the plan has been executed. If a seconds-long run could break the prediction you are about to freeze, run it first. A validation run on different data does not contaminate the confirmatory test.
- Every acceptance criterion has been observed on a real run of the pipeline it judges.

## Write the plan

`docs/science/preregistrations/YYYY-MM-DD-<slug>.md`:

```markdown
# Preregistration: <slug>

Question doc: docs/science/questions/<...>
Data manifest: docs/science/data/manifest.json
Outcome previously inspected by anyone? <no | yes: details, consequence for claim status>

## Hypotheses
- H0: ...
- H1 (directional where justified): ...

## Primary analysis (exact)
- Model/test: <e.g. OLS: outcome ~ exposure + age + site, robust SE>
- Variables and operationalisation: ...
- Transformations: ...
- Inclusion/exclusion rules (fixed now, including outlier rules): ...
- Missing-data handling: ...
- Covariates (fixed now): ...
- Software + versions, seed: ...

## Prediction
- Direction: ...
- Expected magnitude, with source from the survey: ...

## Decision rule
- Confirm H1 if: <exact criterion, written so it does not depend on the result>
- Disconfirm if: <exact criterion>
- Inconclusive if: <e.g. CI includes both the null and the smallest effect of interest>

## Sample size and stopping
- N fixed in advance, with power calculation (alpha, power, assumed effect + source)
- No optional stopping, no peek-and-extend

## Multiplicity
- Number of confirmatory tests, correction (or single pre-specified primary)

## Robustness checks (pre-specified)
- <alternative specifications that will be reported regardless of outcome>

## Exploratory analyses (will be labelled exploratory)
- ...

## Deviation policy
- Any deviation is recorded in docs/science/deviations/ and makes the affected analysis exploratory.
```

## Check falsifiability

State the result that would make you drop H1. If none could, the prediction is unfalsifiable: reframe before freezing.

## Freeze

```bash
python <skill-dir>/scripts/prereg.py freeze docs/science/preregistrations/<file>.md \
    --data data/raw --outputs results
```

This commits **only** the plan and a checksum file of the raw data, in a commit with message `prereg-freeze: <path>`; anything else you have staged is left alone. It refuses if files already exist under `--outputs`, or if the plan already has commits (a frozen plan is never re-frozen; write a new dated plan instead).

Verify at any time, and **always before reporting a confirmatory claim**:

```bash
python <skill-dir>/scripts/prereg.py audit docs/science/preregistrations/<file>.md --data data/raw --outputs results
```

Audit checks from git history alone that (1) the plan was frozen in a `prereg-freeze:` commit, (2) it was never edited afterwards, (3) no file under the outputs dir was committed at or before the freeze, and (4) the data checksums still match.

**Limits, stated honestly:** git history can be rewritten by anyone with the repo. For high-stakes work, push the freeze commit to a remote you do not control, tag it, or deposit the plan in an external registry (OSF, AsPredicted). The audit also cannot detect that you *looked* at results without committing them; that part is discipline.

## Rationalisations to refuse

| Excuse | Reality |
|---|---|
| "Too simple to preregister" | A quick t-test has forking paths too. Writing it takes minutes. |
| "I'll register after a quick look" | The look is the violation. |
| "This covariate obviously belongs" | Put it in the plan before seeing the result, or it is a researcher degree of freedom. |
| "The cutoff that works is the right one" | Choosing a threshold by its result is p-hacking. |
| "It would have been my prediction anyway" | Then writing it first cost nothing. |
| "Just one more specification" | Another fork. List it as exploratory. |
| "Stopping early, it's already significant" | Optional stopping inflates false positives. Honour the fixed N. |

## Handoff

Frozen and audited → `/run-analysis`.

Concept credit: the pre-registration-over-TDD framing and the freeze/audit idea follow K-Dense's Science Superpowers (MIT). This implementation is independent.
