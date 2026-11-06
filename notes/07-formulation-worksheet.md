# Formulation Worksheet: Completed

*Oct 28, 2026.*

**Authorship.** Emma wrote Parts 1–4 (sets, parameters, decision variables, objective) and the budget constraint in words, with guiding questions from Claude. Claude completed the rest (the budget constraint in math, the coverage constraint, variable domains, model type, size, assumptions, and sanity tests). Emma reports instructor permission for this. **Disclose it in the AI use statement.**

Decision: with a fixed budget, choose which **independent stores to upgrade** (fridge and produce, about $25k each) and which **towns get a new grocery store** (about $1M each), so that as many rural people as possible live within R miles of fresh food.

---

## Sets
| Symbol | Meaning |
|---|---|
| **H**, indexed by h | Demand points: rural 2020 Census blocks more than R miles from an existing full-service grocer. Example: a block in Anderson Co., TN with 7 people. |
| **S**, indexed by s | Candidate sites: independent small/medium grocers and independent convenience stores (upgrade candidates), plus Census towns and CDPs (new-store candidates). One set is enough, because the site types differ only in cost, and f_s captures that. |
| **N_h = { s ∈ S : d_hs ≤ R }** | Sites within R miles of neighborhood h. "Within" includes exactly R. |

## Parameters
| Symbol | Meaning | Units | Source |
|---|---|---|---|
| **d_hs** | Straight-line distance from neighborhood h to site s | miles | Census block interior points; USDA SNAP store and Census place coordinates |
| **w_h** | People living in neighborhood h | people | 2020 Census |
| **f_s** | Cost to fund site s: $25,000 for a store upgrade, $1,000,000 for a new store in a town | $ | notes/06-cost-parameters.md |
| **B** | Total program budget (base case $3,000,000) | $ | HFFI award figures, notes/06 |
| **R** | Coverage radius (5 or 10) | miles | USDA rural low-access standard (10 mi) |
| *(optional)* **α**, with **ℓ_h ∈ {0,1}** | Extra weight on low-income neighborhoods: replace w_h with w_h(1 + α ℓ_h) in the objective | unitless | SRAM `LowIncomeTracts` |

## Decision variables
| Symbol | Meaning |
|---|---|
| **x_s ∈ {0,1}** | 1 if site s is funded (a store gets the upgrade, or a town gets a new grocery store); 0 otherwise |
| **y_h ∈ {0,1}** | 1 if neighborhood h is covered (at least one funded site within R miles); 0 otherwise |

## Model
**maximize** Σ_{h ∈ H} w_h · y_h  (total people covered)

**subject to**

1. **Coverage:** y_h ≤ Σ_{s ∈ N_h} x_s for every h ∈ H.
   In words: neighborhood h can count as covered only if at least one site within R miles of it is funded. If no nearby site is funded, the right side is 0, so y_h is forced to 0. If N_h is empty, as for the 798 Tennessee people with no candidate within 10 miles, y_h is always 0.
2. **Budget:** Σ_{s ∈ S} f_s · x_s ≤ B.
   In words: total spending on funded sites cannot exceed the budget.
3. **Domains:** x_s ∈ {0,1} for every s ∈ S, and y_h ∈ {0,1} for every h ∈ H (y_h may be relaxed to [0,1], see question 16).

Note on the coverage constraint: it uses "≤ sum," not "= sum." A neighborhood near two funded sites has a right-hand side of 2, but y_h stays at most 1, so its people are counted only once.

## Check yourself
**15. Model type.** An **integer program**, specifically a binary program. The x_s variables must be 0 or 1, because you can't fund 0.4 of a store. If y_h is relaxed to be continuous, it becomes a **mixed-integer linear program (MILP)**. The objective and all constraints are linear. Gurobi solves it with **LP-based branch and bound**: it solves the LP relaxation for an upper bound, branches on fractional x_s, and adds cuts and heuristics. It stops when the best solution found is within the gap tolerance of the bound.

**16. Can y_h be continuous in [0,1]?** **Yes.** The objective maximizes Σ w_h y_h with w_h > 0, so at an optimum each y_h is pushed as high as its constraints allow: y_h = min(1, Σ_{s ∈ N_h} x_s). Once the x_s are integers, that value is 0 or 1. So relaxing y_h does not change the optimal value, and it gives the solver fewer integer variables. This is a good point for the Model Type section of the report.

**17. Size, Tennessee at R = 10 (blocks):**
- Variables: |S| + |H| = 1,351 x-variables + 1,930 y-variables = **3,281**. Only about 400 sites are within R of any demand. The rest could be dropped in preprocessing, or Gurobi's presolve removes them.
- Constraints: |H| coverage + 1 budget = **1,931**.
- Nonzeros: about 13,803 coverage pairs plus |H| + |S| other terms, so the matrix is very sparse.
- For comparison, all of Appalachia at R = 5 has about 166k y-variables and 600k coverage pairs.

**18. Assumptions:**
1. **Distance:** straight-line distance stands in for travel distance. In the mountains, real driving distance is longer, so coverage is optimistic.
2. **Location:** everyone in a census block lives at the block's interior point.
3. **Coverage:** "covered" means within R miles. A neighborhood counts fully or not at all, with no partial credit for being slightly farther away.
4. **Costs:** costs are the same everywhere within a site type. Upgrade and new-store costs come from programs in California, Ohio, North Carolina, and Kansas, not from Appalachia.
5. **Capacity:** a funded site can serve everyone within R miles. There are no capacity limits.
6. **Participation:** every candidate store accepts an upgrade if offered, and a new store in a town is viable. In reality, stores can decline and new stores can fail.
7. **Fixed baseline:** existing full-service grocers stay open, and demand is defined relative to them (people more than R from a current grocer).
8. **Chain identification:** a store is a chain if its name appears at 20 or more SNAP stores nationally. Chains and dollar stores are not funded.
9. **Static, one-time decision:** no timing, operating costs, or multi-year budget.

## Sanity tests (run these in the notebook)
- **B = 0:** covered people = **0**, since nothing can be funded.
- **B huge** (for example $1 billion): covered people = **40,599** for Tennessee at R = 10, which is everyone who has at least one candidate site within R (41,397 − 798). This matches `coverable_pop_excl_dollar` in `instance_summary.csv`.
- **Upgrades only:** coverage goes **down or stays the same**. Removing site options shrinks the feasible set, so the optimum can't improve.
- **Raising R:** with demand held fixed, coverage can only go **up or stay the same**, because each N_h gets bigger. In our data, though, demand itself changes with R (only blocks more than R from a grocer count), so compare R = 5 and R = 10 by the **percentage** of demand covered.
- **Independent recount:** the solver's objective should equal `people_covered` from the `verify()` cell in the notebook.
