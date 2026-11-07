---
name: validate-pipeline
description: Prove an analysis pipeline can detect a known effect and report a null before running it on real data - positive controls, negative controls, parameter recovery, unit tests for transforms. Use before preregistering or running any non-trivial analysis, model, simulation, or custom statistic.
license: MIT
---

# Validate Pipeline

A pipeline that has never been shown to find a known effect, or to stay quiet on pure noise, produces numbers with no meaning. This is the scientific equivalent of watching the test fail for the right reason.

Validation uses **simulated data or data that is not the confirmatory outcome data**, so it never contaminates the test.

## Checks, in order

1. **Unit tests for transformations.** Every function that cleans, scales, joins, bins, converts units or encodes variables gets a test on a tiny hand-checkable input. Include the cases where science goes wrong: missing codes (`-999`), zero/negative values under a log, timezone boundaries, off-by-one (0- vs 1-based) indexing, group-by on the wrong key.
2. **Known answers.** If a published or analytic reference exists (a textbook example, a standard dataset with known coefficients, a closed-form limit, a conservation law, a dimensionless check), reproduce it to a stated tolerance. Cite where the reference value comes from, and verify the source (`source-verification`).
3. **Negative control / null simulation.** Generate data with no effect (shuffle the outcome, or simulate from the null) and run the full pipeline hundreds of times. The false-positive rate must match the nominal alpha; interval coverage must match its nominal level. If it does not, the pipeline is broken or an assumption is violated.
4. **Positive control / parameter recovery.** Simulate data with a known effect of realistic size and noise, matched to the real data's structure (clustering, missingness, sample size, distribution). The pipeline must recover the parameter without bias, and the power must match the plan's power calculation.
5. **Sensitivity to nuisance choices.** Perturb things that should not matter (row order, column order, seed, platform where feasible). Results must be stable within tolerance. If they are not, find out why before proceeding.
6. **Leakage check.** Deliberately permute labels *before* the preprocessing/feature-selection step. A leak-free pipeline then performs at chance. Above-chance performance means information is leaking.
7. **Cheapest falsification.** Run the smallest end-to-end run that could break the plan's central assumption. Do it before freezing.

## Evidence required

Record in `docs/science/validation/<slug>.md`: what was tested, simulation settings and seeds, the command, the numeric result, the tolerance, and pass/fail. Show actual output, not "it passed". A claimed pass without shown output is a fail.

Create the validation scripts in the repo so they re-run in CI; they are part of the analysis, not a one-off.

## When validation fails

Do not tune the pipeline until the failure goes away without understanding it. Follow `diagnosing-results`: the failure is the finding. Fix the cause, then rerun every check, not just the one that failed.

## Done when

Checks 1-4 pass with shown evidence (5-7 where applicable), and the validation scripts are committed. Hand off to `preregister`.
