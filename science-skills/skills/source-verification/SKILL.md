---
name: source-verification
description: Verify that every cited source exists, says what the claim attributes to it, and has not been retracted. Use whenever a citation, statistic, quote, or "studies show" claim is about to enter a survey, plan, or report, or when the user asks if a reference is real.
license: MIT
---

# Source Verification

Language models produce plausible citations that point to real papers that do not contain the claim, to real authors who never wrote it, or to nothing at all. Treat every citation as unverified until you have opened the source and found the claim in it.

## The ledger

Maintain `docs/science/sources/ledger.md`. One row per **claim-source pair**, not per source: the same paper can support one claim and not another.

| ID | Claim as used | Source (DOI/URL/accession) | Locator (page, table, line) | Status | Checked by / date | Note |
|---|---|---|---|---|---|---|

Status values, and nothing else:

- **verified**: opened the source, found the claim at the stated locator, wording and numbers match.
- **partial**: source supports a weaker or narrower claim. Rewrite the claim to match the source.
- **unverifiable**: could not open the full text. The claim may be used only if labelled "reported in abstract" or dropped.
- **contradicted**: the source says something different. Remove or correct the claim.
- **not found**: no such source. Remove it. Do not search for something that "might fit".

## Procedure

1. **Resolve the identifier.** Run `scripts/check_dois.py` on a file of references. It extracts DOIs, queries Crossref, and prints the registered title, year and journal so you can compare them to the citation. If the network is blocked it reports `UNCHECKED`, which is not a pass.
2. **Open the full text** (or the dataset, registry entry, or standard). Abstract-only is not verification.
3. **Find the claim.** Locate the sentence, table or figure. Record the locator. Check numbers digit by digit, including units, population, and whether the figure is an estimate, CI bound, or p-value.
4. **Check the direction and scope.** Does the source show it, or only mention it as background, a hypothesis, or someone else's result? Follow citation chains to the study that actually measured it.
5. **Check status.** Look for retractions, corrections, expressions of concern, and later failed replications (publisher page, Crossref `updated-by` data, retraction databases). A retracted study cannot support a claim.
6. **Check independence.** Ten articles repeating one original result are one source. Identify the original.
7. **Check the effect size and sample**, not just the headline. Small-N, single-site, non-randomised and non-replicated results are weak evidence even when real.

## Hard rules

- Never output a citation you have not verified in this session or that is not already `verified` in the ledger.
- Never fill in a DOI, page number, or author list from memory.
- Never quote: paraphrase and point to the locator, unless the exact wording matters and you have it open.
- Quote-level claims ("the authors state that...") need the exact text copied from the opened source.
- If a source is paywalled and you cannot open it, say so and ask the user to supply it. Do not infer its contents.
- A search result snippet is not the source.

## When this skill is done

The ledger has no row with a status that the claim as written cannot support, and every sentence in the downstream document that cites a source has a ledger row.
