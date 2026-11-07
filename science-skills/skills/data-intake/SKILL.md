---
name: data-intake
description: Receive a new dataset safely - make raw data immutable and checksummed, document provenance and units, check schema and missingness, and profile it without looking at the relationship under test. Use whenever a dataset arrives, before any modelling.
license: MIT
---

# Data Intake

Most wrong results are data problems wearing a statistical costume. Intake makes the data trustworthy, and keeps you blind to the outcome until the analysis is frozen.

## 1. Freeze the raw data

- Raw files go in the configured raw dir (`data/raw/` by default). **They are never edited, only added to.** Cleaning produces new files elsewhere.
- Run `scripts/manifest.py <files or dirs> -o docs/science/data/manifest.json`. It records sha256, size, and for delimited files the row count and header. Commit the manifest.
- Make files read-only if the platform allows (`chmod a-w`).
- Record provenance in `docs/science/data/<dataset>.md`: source, who collected it, when, how, version/accession, retrieval date and command, license, consent/privacy constraints. If you cannot say where it came from, say so; that is a finding.

## 2. Data dictionary

For every column: name, meaning, **unit**, type, allowed range, how missing is encoded (`NA`, `-999`, empty, `0`?), and whether it is an **outcome**, **exposure**, **covariate**, **identifier**, or **post-treatment/post-outcome** variable. Ask the user for what you cannot infer; do not guess units.

## 3. Structural checks (allowed before the freeze)

Check things that do not reveal the relationship under test:

- Schema: expected columns present, types parse, no duplicated header rows
- Row-level: duplicate rows and duplicate IDs, impossible values (negative ages, dates in the future, percentages > 100), unit mixing (kg vs g, dB vs linear)
- Missingness **pattern** per column and whether it is structured (by site, by time, by arm)
- Timestamps: timezone, ordering, gaps, daylight-saving jumps
- Group sizes and balance on **covariates**
- Sampling: how rows were selected, and what is systematically absent (survivorship, selection)
- Encoding: character set, locale decimal separators, Excel mangling (gene names to dates, leading zeros stripped, 15-digit truncation)

## 4. The blind-profile rule

Until `preregister` has frozen the plan:

- Profile covariates, structure and missingness freely.
- **Do not** plot, tabulate or correlate the outcome against the exposure or any candidate predictor. Do not fit models. Do not compute the effect.
- If the user has already looked at the outcome, record it in the dataset note ("outcome previously inspected by <who>, <when>"). That limits what claims this data can confirm; `preregister` must account for it. Prefer a held-out split, a new sample, or labelling everything exploratory.
- If a split is needed, create it **now**, with a recorded seed, before any outcome inspection. Store split assignments as a file. Never re-split after seeing results.

## 5. Leakage review

List every variable and ask: *would this be known at the time the prediction or decision is made?* Flag identifiers that encode the outcome, post-treatment variables, future information, duplicated entities across train/test (same patient, same sample, same document), and normalisation fitted on the full data before splitting.

## 6. Output

`docs/science/data/<dataset>.md` containing provenance, dictionary, structural findings, the leakage review, the split policy, and **open data-quality questions for the user**. Done when the manifest is committed and verifies, the dictionary contains no guessed values, and every open question is answered by the user or recorded as open. Hand off to `validate-pipeline` or `preregister`.
