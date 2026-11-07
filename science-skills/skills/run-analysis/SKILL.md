---
name: run-analysis
description: Execute a frozen preregistered analysis exactly as written, in a pinned reproducible environment, with deviations recorded and exploratory work labelled. Use once a preregistration is frozen and audited.
license: MIT
---

# Run Analysis

Run what was registered. Nothing more, nothing less.

## Gate

Do not start until all four are true. Check them, do not assume:

1. `prereg.py audit <plan>` passes (see `preregister`)
2. `docs/science/data/manifest.json` verifies: `python <data-intake>/scripts/manifest.py <raw-dir> --verify docs/science/data/manifest.json`
3. The environment is pinned and the provenance is captured (`reproducible-compute`)
4. The pipeline passed `validate-pipeline`, or the plan states why it was waived

If any fail, stop and say which. If the plan is not frozen, everything from here is exploratory: say so, and offer to freeze first.

## Execute

1. Turn the plan's primary analysis into a **script** (or a notebook that runs top to bottom from a clean kernel). One entry point, no manual steps, all paths relative, seed set from the plan.
2. Run the **primary analysis first**, unchanged, and write results to the outputs dir with the commit hash and run id in the filename or header.
3. Run the **pre-specified robustness checks**. Report them whatever they show.
4. Apply `statistical-discipline` to what you computed: assumptions, effect sizes with intervals, multiplicity.
5. Run `reproducible-compute`'s clean-room check: re-execute from scratch in a fresh directory and compare.

**If your harness can spawn subagents**, give each analysis step to a fresh subagent that receives only the plan section, the data manifest and the previous step's output, not your reasoning or your hopes. Review each result in two passes: (a) **protocol**: did it run exactly what was registered, nothing more? (b) **rigor**: assumptions, leakage, correctness, reproducibility. A subagent that "helpfully" adds an unregistered analysis has produced an exploratory result; label it.

## Log as you go

Append a `lab-notebook` entry after every run, reported or not, with the commit and data checksum. The count of analyses tried is what multiplicity correction and honest reporting depend on.

## Deviations

Anything that differs from the plan (a model that failed to converge, a column that turned out to be mis-coded, an assumption violated) goes in `docs/science/deviations/YYYY-MM-DD-<slug>.md`:

```markdown
What the plan said: ...
What happened: ...
What was done instead: ...
Why (reason must not depend on the outcome): ...
Effect on claim status: the affected analysis is now exploratory | unaffected (justify)
```

A change motivated by what the result looked like is not a deviation, it is p-hacking. Stop and relabel.

## Exploratory work

Allowed and valuable. Put it in a separate script and a separate output folder named `exploratory/`. It generates hypotheses for the *next* preregistration. It never appears in the confirmatory results.

## Anomalies

If a result looks wrong, too good, or implausible → `diagnosing-results` **before** changing anything. Never drop data, change a threshold, or rerun with a different seed to make an anomaly go away.

## Done when

Primary and robustness results exist, deviations are logged, the clean-room rerun matches, and nothing in the outputs dir is unlabelled. Hand off to `/red-team`.
