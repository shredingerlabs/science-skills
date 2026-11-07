---
name: statistical-discipline
description: Checklist for sound statistical analysis - estimand-to-method fit, assumptions, effect sizes with intervals, multiplicity, leakage, pseudoreplication, missing data, and honest uncertainty. Use whenever computing or interpreting a p-value, confidence interval, model fit, or comparison, or reviewing someone else's statistics.
license: MIT
---

# Statistical Discipline

Apply while analysing and while reviewing. Statistics here is a set of guards against fooling yourself; `REFERENCE.md` has the detail for each item. Where the plan is frozen, these checks apply to the plan's own method: do not swap methods because one gives a better answer.

## Before fitting

- **Method follows estimand.** The test must answer the question in the plan. A t-test on data with repeated measures per subject does not.
- **Unit of analysis.** What is the independent unit? Cells from one animal, rows from one patient, reads from one sample, pixels from one image are **not** independent. Model the clustering (mixed model, cluster-robust errors, aggregate to the unit). Pseudoreplication is the most common fatal error.
- **Sample size and power** were fixed in advance from a sourced effect size. If power is low, say so: a null from an underpowered test is uninformative, not evidence of absence.
- **Assumptions** stated in the plan (distribution, independence, equal variance, linearity, proportional hazards) and the diagnostics chosen to check them. Check them **on residuals/design**, not by testing the outcome-exposure relation.
- **Outlier and exclusion rules** are written before looking. Excluding a point because it hurts the result is p-hacking.

## While fitting

- **One primary analysis.** Everything else is secondary/exploratory and reported as such.
- **Splits and CV are leak-free.** Fit all preprocessing (scaling, imputation, feature selection, hyperparameter tuning) **inside** the training fold only. Group splits by entity (patient, site, protein family, document). Never tune on the test set; if you did, it is no longer a test set.
- **Never choose the model by its test-set performance** and then report that performance as an estimate.
- **Missing data:** state the mechanism you assume (MCAR/MAR/MNAR) and why; complete-case analysis is an assumption, not a default.
- **Multiplicity:** count every test you ran, including ones you did not report. Correct, or pre-specify one primary.
- **Seeds:** results that change with the seed are telling you about their noise. Report variability across seeds/resamples.

## Reporting

- **Effect sizes with intervals, in the units of the question.** Not "p < 0.05", not "significant". Say how big, and how uncertain.
- **Distinguish** statistical from practical significance; absence of evidence from evidence of absence (use equivalence tests or CIs against the smallest effect of interest).
- **p-values** are the probability of data this extreme under the null, not the probability the hypothesis is true or false. Do not report p = 0.000; report p < 0.001.
- **Show the data**, not only summaries: plot individual points and distributions. Bar charts of means hide the evidence.
- **Report what you tried.** Number of models, specifications, and subsets examined. A specification curve or the pre-specified robustness table beats a single hand-picked result.
- **Language matches design.** Observational data → associations, not "causes", unless a defensible causal design (and its assumptions) is stated.
- **Check for Simpson's paradox:** does the effect hold or reverse within important subgroups or strata?
- **Regression to the mean, survivorship, selection, immortal-time and collider biases** each have a short entry in `REFERENCE.md`; read the relevant ones for the design at hand.

## When you find a violation

State it, quantify its likely effect, and either fix it (if the plan permits), record a deviation (`run-analysis`), or label the result exploratory. Never "fix" it silently.

Further detail and a pitfalls table: `REFERENCE.md`.
