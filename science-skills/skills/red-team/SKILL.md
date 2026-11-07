---
name: red-team
description: Independent adversarial review of an analysis or report by a fresh reviewer who did not produce it - protocol compliance, statistical rigor, clean-room reproduction, and claim-vs-evidence - followed by a rigorous response to findings. Use before reporting results, after a frozen analysis completes, or when a reviewer comment arrives.
license: MIT
---

# Red Team

The author cannot grade their own work: the same blind spots that produced the error hide it. Review is only independent if the reviewer **did not see the author's reasoning, cannot edit the analysis, and is trying to break it.**

## Independence rules

1. **Fresh context.** Dispatch a new subagent (the `science-reviewer` agent, if installed from this pack; otherwise a general read-only subagent) that has **none** of the author's conversation history.
2. **Artifacts, not narrative.** The reviewer receives only: the question doc, the frozen preregistration, the deviation log, the data manifest and dictionary, the code, the provenance records, the outputs, the source ledger, and the draft report. It does **not** receive the author's explanations, hopes, or "what the result means".
3. **Read-only on the analysis.** The reviewer may run code in a **scratch copy** (clean-room rerun) and write only to `docs/science/reviews/`. It never edits the analysis, plan, or data.
4. **Different model where possible**, per the setting in `docs/science/CONFIG.md`. Same-model review shares blind spots; note it in the review if unavoidable.
5. **Run three reviewers in parallel**, one per axis, so none pollutes another:

| Axis | Question | Method |
|---|---|---|
| **Protocol** | Did the analysis do exactly what was frozen, nothing more? | Run `prereg.py audit`; diff plan vs code vs outputs; check every deviation is logged and its claim-status consequence applied; look for unregistered analyses presented as confirmatory |
| **Rigor** | Are the statistics, data handling, and computation sound? | Apply `statistical-discipline`'s checklist; hunt for leakage, pseudoreplication, multiplicity, unit errors; **clean-room rerun** from a fresh clone and compare outputs within tolerance; re-derive 2-3 headline numbers independently |
| **Claims** | Does every claim in the report follow from the evidence and verified sources? | For each claim in the draft, locate the evidence row in the claim ledger; open the cited source and find the claim (`source-verification`); check wording vs design (causal verbs on observational data), overgeneralisation, missing uncertainty, omitted null results |

## Reviewer's brief (give this verbatim to each reviewer)

> You are an adversarial reviewer. Your job is to find the strongest reasons this analysis should not be believed. Assume nothing is correct until you have checked it yourself. Do not trust summaries, comments, or the report's description of what the code does: read the code and run it. For each finding give: **severity** (fatal / major / minor), **location** (file:line, table, figure, ledger row), **evidence** (command and output, or the specific text), **why it matters**, and **how to check the fix**. Distinguish clearly between "I verified this is wrong" and "I suspect this might be wrong". Do not soften findings, and do not invent problems: if an axis is clean, say what you checked to conclude that. Finish with the three analyses you would run next if you wanted to overturn the main conclusion. Write your findings to `docs/science/reviews/<date>-<axis>.md`.

Stakes set the depth (from `CONFIG.md`): *exploratory* - protocol + a rerun; *internal decision / publication* - all three axes; *clinical or safety-relevant* - all three plus a second independent reviewer on the claims axis and a human domain expert sign-off that the agent cannot supply.

## Receiving the review

For every finding, respond with exactly one of:

- **Fixed**: what changed, the commit, and the check that now passes. Rerun everything downstream.
- **Rebutted**: the evidence (not an assertion) that the finding is wrong. The reviewer re-checks the rebuttal.
- **Accepted as limitation**: the finding stands and goes into the report's limitations, with its effect on the claim.

Not allowed: "good catch!" without a change; blanket agreement; fixing the symptom a reviewer named while leaving its cause; changing the analysis in response to a finding **and keeping the confirmatory label** (a change after review is a deviation: log it, and relabel the affected result exploratory); dismissing a finding because it is inconvenient to the hypothesis.

Record the finding→response table in `docs/science/reviews/responses.md`. **Fatal and major findings block `/report-findings`** until each is fixed, rebutted with accepted evidence, or the claim is withdrawn.

## What the review cannot do

An agent review cannot replace domain-expert judgement, ethics review, or independent replication on new data. It reduces avoidable error; it does not certify truth. Say so in the report's limitations.
