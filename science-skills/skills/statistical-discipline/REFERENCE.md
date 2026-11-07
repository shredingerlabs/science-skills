# Statistical pitfalls - reference

Load the rows relevant to the design at hand. Each row: what goes wrong, how to detect it, what to do.

## Inference

| Pitfall | Detect | Do |
|---|---|---|
| **Pseudoreplication** (non-independent units treated as independent) | Ask "what was randomised / sampled independently?" Count that, not rows. | Aggregate to the unit, or mixed/cluster-robust model with the correct grouping. |
| **p-hacking / forking paths** | More than one specification tried; choices made after seeing results | Preregister one primary; list all tried; correct or label exploratory. |
| **HARKing** | Hypothesis worded after results; "as expected" for an unexpected finding | Compare to the frozen plan; relabel exploratory. |
| **Optional stopping** | Sample size not fixed; "collected until significant" | Fixed N, or a pre-specified sequential design with proper alpha spending. |
| **Multiple comparisons** | Count of tests > 1 for a family of hypotheses | Bonferroni/Holm for family-wise, Benjamini-Hochberg for FDR, stated in advance. |
| **Low power / winner's curse** | Small N, large "significant" effect | Report CI; expect the true effect to be smaller; plan replication. |
| **Equating non-significant with no effect** | "No difference was found" from a wide CI | Equivalence test, or CI against the smallest effect of interest. |
| **Difference in significance ≠ significant difference** | "Significant in A, not in B, so A differs from B" | Test the interaction/difference directly. |
| **Dichotomising a continuous variable** | Median splits, arbitrary cutoffs | Keep continuous; if a cutoff is needed, justify before seeing results. |
| **Regression to the mean** | Selection on an extreme baseline, then improvement | Include a control group; do not attribute change to the intervention. |
| **Base-rate neglect** | Positive predictive value from a test with low prevalence | Report PPV/NPV with the actual prevalence. |
| **Ecological fallacy** | Group-level pattern inferred for individuals | Restrict claims to the level analysed. |
| **Simpson's paradox** | Aggregate trend differs from within-stratum trend | Stratify on the pre-specified key variable; draw the DAG. |
| **Collider / post-treatment adjustment** | Adjusting for a variable caused by exposure or outcome | Adjust only for pre-exposure confounders per a stated causal diagram. |
| **Survivorship / selection bias** | Only completers, successes, or retained samples observed | Describe how units entered the sample; quantify what is missing. |
| **Immortal time bias** | Exposure defined by a future event in a cohort | Align time zero; use time-varying exposure. |

## Prediction / machine learning

| Pitfall | Detect | Do |
|---|---|---|
| **Preprocessing leakage** | Scaling/imputation/feature selection fit before the split | Fit inside the training fold (pipeline object). |
| **Entity leakage** | Same patient/site/protein/document in train and test | Group-wise split. |
| **Temporal leakage** | Future information in features or random split of time series | Split by time; only past features. |
| **Target leakage** | Feature derived from, or recorded after, the outcome | Review every column against "known at prediction time?" |
| **Test-set reuse / tuning on test** | Many models compared on the same held-out set | Nested CV, or a fresh locked-away test set used once. |
| **Metric mismatch** | Accuracy on imbalanced data; R² on extrapolation | Choose metric from the decision; report baseline (majority class, mean, naive forecast). |
| **No baseline** | A model reported alone | Always report a trivial baseline and the strongest simple model. |
| **Uncertainty omitted** | One score from one split and one seed | Repeated resampling; intervals; variance across seeds. |
| **Overfitting hyperparameter search** | Best-of-N reported as the estimate | Report performance on data not used in the search. |
| **Distribution shift ignored** | Train and deployment populations differ | Evaluate on a shifted split; state the scope. |

## Computational

| Pitfall | Detect | Do |
|---|---|---|
| **Unit/scale mixing** | dB vs linear, 0/1-based, g vs kg, local vs UTC | Unit-tested conversions; use a units library where possible. |
| **Floating point and summation order** | Results differ across machines or thread counts | Set tolerances; pin threads; compare with tolerance not equality. |
| **Silent NaN/inf propagation** | Means unchanged after a pipeline step that should have changed them | Assert on NaN counts at stage boundaries. |
| **Seed dependence** | Conclusion flips with seed | Report across seeds; increase iterations; do not pick a seed. |
| **Convergence ignored** | Optimiser warnings, boundary estimates | Treat as a failed fit; diagnose; record a deviation. |
| **Join explosion / silent row loss** | Row counts differ before/after merge | Assert row counts and key uniqueness at every join. |

## Reporting checks

- Every figure: axes labelled with units; n shown; uncertainty shown; individual points where feasible.
- Every number in the text traces to a script and a commit.
- Every "significant" is accompanied by an effect size and interval.
- Confirmatory and exploratory results are in separate sections.
