---
name: grill-hypothesis
description: Get interviewed until a vague research interest becomes a falsifiable question with a defined estimand, comparator, and disconfirming result. Use before touching any data, when the user has a hunch, a dataset and a loose question, or says "does X affect Y".
license: MIT
---

# Grill Hypothesis

Interview the user until the question is falsifiable. **Hard gate: do not load, plot, summarise or model any outcome data until the user approves the final question.** Looking is what turns a confirmatory study into a story told afterwards.

Structural metadata (column names, row counts, file formats) may be read. Anything that shows the relationship under test may not.

## Method

Work a **design tree**, in rounds. Ask every question whose prerequisites are already settled, numbered, each with your recommended answer; word it so "yes" accepts your recommendation. Wait for answers, then recompute the frontier. Finding facts (what the files contain, what the literature says) is your job: look them up, do not ask.

Branches to cover:

1. **Claim.** What is the user hoping is true, in one sentence? Name it as a hope. The agent's job is to find out whether it survives.
2. **Estimand.** Exactly what quantity? Effect of what, on what, in whom, measured how, compared to what? Causal ("would reduce") vs associational ("is linked to") vs predictive ("forecasts")? Each has a different design and different words allowed in the report.
3. **Comparator.** Against what is the effect measured? A claim without a counterfactual is not testable.
4. **Disconfirming result.** "What result would make you drop this?" State it as a number or pattern. If nothing could, the claim is unfalsifiable: sharpen or drop it.
5. **Confounders and alternative explanations.** Name at least three rival explanations. Which can the data rule out?
6. **Data in hand vs needed.** What exists, who collected it, how, why, and has anyone (including the user) already looked at the outcome? If yes, record it: that data cannot give a clean confirmatory test.
7. **Confirmatory vs exploratory.** Which parts are tests of a prior prediction, which are open searching? Be explicit that exploratory findings are leads.
8. **Stakes and constraints.** What decision rides on this? Ethics, privacy, consent, licensing.
9. **Smallest informative study.** Is there a cheaper design that could falsify the claim sooner?

Done when the frontier is empty and the user confirms the written question.

## Output

Write `docs/science/questions/YYYY-MM-DD-<slug>.md`:

```markdown
# Question: <slug>

**Claim (hoped):** ...
**Question (falsifiable):** ...
**Estimand:** <quantity, population, comparator, outcome, time window>
**Type:** causal | associational | predictive
**Would be dropped if:** <specific disconfirming result>
**Rival explanations:** 1) ... 2) ... 3) ...
**Data:** <sources, who collected, outcome already seen? yes/no>
**Confirmatory:** ...
**Exploratory:** ...
**Stakes:** ...
**Open items:** ...
```

Then hand off: `survey-literature` for prior work, or `data-intake` if the data is already in hand.
