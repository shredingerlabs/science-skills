---
name: reproducible-compute
description: Make an analysis re-runnable by someone else - pinned environment, seeded randomness, immutable raw data, scripted pipeline, captured provenance, and a clean-room rerun check. Use when setting up an analysis workspace, before running the frozen plan, and before reporting any number.
license: MIT
---

# Reproducible Compute

"Works on my machine, this session, in this notebook state" is not a result. A number is reproducible when a stranger can recreate it from the repo, the raw data and one command.

## Workspace

1. **Pinned environment.** Create a lockfile and commit it: `uv.lock`/`requirements.txt` with hashes, `renv.lock`, `conda-lock.yml`, or a container with pinned base image digest. Install **from the lockfile**, not from "latest". Record the interpreter version.
2. **Immutable raw data.** Raw data is read-only; every derived file is produced by a script from raw. Never hand-edit an intermediate file. Verify with `data-intake`'s `manifest.py --verify` at the start of every run.
3. **Scripts, not state.** One entry point (a script, `make`, `snakemake`, `nextflow`, `just`), parameters in a config file, all paths relative to the repo root, no absolute paths, no credentials in code. Notebooks are allowed only if they run top to bottom from a fresh kernel; restart-and-run-all before trusting them.
4. **Every source of randomness seeded**, from one seed in config: Python `random`, NumPy `Generator` (prefer `default_rng(seed)` passed explicitly), the ML framework, data-loader workers, train/test splitters, hash seeds (`PYTHONHASHSEED`). Pass RNGs as arguments; avoid hidden global state. Seeds are chosen **before** seeing results. Do not hunt for a seed.
5. **Nondeterminism acknowledged.** Multithreaded BLAS, GPU kernels, parallel reduction order and some library versions change floating-point results. Pin thread counts, enable deterministic modes where available, and compare with an explicit tolerance rather than equality. State the tolerance.
6. **Large or slow steps cached by content hash**, never by "file exists", so a changed input invalidates the cache.

## Capture provenance, every run

```bash
python <skill-dir>/scripts/capture_env.py -o results/provenance.json \
    --seed <seed> --cmd "<the exact command>" --manifest docs/science/data/manifest.json
```

It records commit, dirty flag, interpreter, platform, installed packages, lockfile hashes, data manifest hash, thread-related env vars. **If the dirty flag is true, the run is not reproducible from its commit**: commit first, then run.

Each output file names (or sits beside) the provenance record of the run that made it. A figure or number without one is an unsourced claim.

## Clean-room rerun (required before reporting)

```bash
rm -rf /tmp/rerun && git clone . /tmp/rerun && cd /tmp/rerun
# restore raw data (read-only copy), install from the lockfile, run the single entry point
```

Compare the new outputs to the originals, file by file, with the stated tolerance. Differences must be **explained**, not waved away: environment drift, hidden state, an unseeded RNG, an absolute path, an undeclared dependency. Record the comparison in `docs/science/reports/reproduction.md`.

If a clean rerun is impossible (proprietary data, cluster-only compute), say exactly why and what a reader would need.

## Archive

At the end, the following must exist together and be citable: code at a tagged commit, lockfile, config, data manifest (and data or the instructions to obtain it), provenance records, frozen preregistration, deviation log, review log. Offer to tag the commit and, for publication, to prepare a deposit (Zenodo, OSF) with a DOI.

## Red flags

"It's deterministic, I didn't set a seed." "Just install the latest version." "I edited the CSV in Excel." "Rerun the cell above." "The notebook has hidden state but the figure is right." Each of these means: not reproducible yet.
