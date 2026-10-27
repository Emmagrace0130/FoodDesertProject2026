# IE 522 Final Project Plan: Optimizing Fresh-Food Access in Rural Appalachia

*Draft plan, Oct 27, 2026. Targets Option 1 (own problem, up to +10 extra credit). Due Wed Dec 9, 11:59 PM.*

## The problem in one sentence
A funder has a fixed budget to bring fresh food closer to rural Appalachians who live far from a full-service grocery store. It can fund **fresh-produce upgrades at existing stores**, such as coolers and produce sections in dollar or small stores (cheap), or **new full-service grocers** (expensive). **Which sites should it fund to cover as many people as possible?**

- **Decision maker:** a state health department, a regional food bank, or a Healthy Food Financing Initiative-style funder.
- **Why it's realistic:** all the data is public and already in this repo. The setting comes straight from our finding that 464,000 rural Appalachians count as having food access only because of a dollar store.
- **Why it's new:** the earlier descriptive analysis (notes 01–03) only *measures* the gap. The IE 522 work is the *decision model* built on top of it. The report intro must say this, because the spec requires stating overlap with other work.

## Data (already in the repo)
| Model piece | Source | Size (rural ARC Appalachia) |
|---|---|---|
| Demand points *i* and population *w_i* | 2020 Census blocks more than 10 mi from a full-service grocer | 25,015 blocks, 489,657 people |
| Aggregated demand (alternative) | Same, rolled up to block groups | 1,502 block groups |
| Low-income weight | SRAM `LowIncomeTracts` flag | per tract |
| Candidate upgrade sites *j* | 2025 SNAP dollar stores (other small stores could be added) | 1,965 within 10 mi of uncovered demand |
| Candidate new-grocer sites | Town centers or block-group centroids (to choose) | a few hundred |
| Existing full-service grocers | 2025 SNAP data | 3,730 in or near the region |
| Distances *d_ij* | Straight-line now; driving distance optional (OSRM) | sparse, within radius *R* |
| Costs *c_j* | **Still needed:** cited figures for a store produce upgrade vs a new rural grocery store | find sources |

Tennessee-only instance, for a smaller case: 705 dollar stores, 428 full-service grocers, 3.0M people in ARC Tennessee.

## Core model: budgeted maximal covering location problem (MIP)
**Sets**
- *I*: uncovered demand points
- *J*: candidate sites
- *N_i ⊆ J*: sites within *R* miles of demand point *i*

**Parameters**
- *w_i*: people at demand point *i* (optionally weighted up, by a factor α, when the point is in a low-income tract)
- *c_j*: cost to fund site *j* ($)
- *B*: total budget ($)
- *R*: coverage radius (mi)

**Variables**
- *x_j* ∈ {0,1}: fund site *j*
- *y_i* ∈ {0,1}: demand point *i* is covered

**Model**
- Maximize Σ_i w_i y_i (people covered)
- subject to
  - y_i ≤ Σ_{j ∈ N_i} x_j for every *i* (a point counts as covered only if a funded site is within *R*)
  - Σ_j c_j x_j ≤ B (budget)
  - x, y binary

**Model type:** integer program. The constraint matrix is sparse, and *y* can be relaxed to 0 ≤ y ≤ 1 without changing the optimum.

**Software:** Pyomo or gurobipy, with HiGHS (free) or Gurobi (free academic license). Check what the course uses.

## Candidate approaches (spec section 4: at least two, compared)
1. **Exact MCLP MIP** (recommended main approach): optimal or with a proven gap, easy to explain, runs in seconds to minutes at this size.
2. **Greedy heuristic:** repeatedly fund the site with the most newly covered people per dollar. Fast and intuitive, with a known worst-case guarantee for coverage problems, but no optimality proof.
3. **p-median MIP:** minimize total people-weighted distance instead of coverage. Better for equity in distance, but much larger, since it needs an assignment variable for every demand–site pair; aggregation is needed at full scale.
4. **LP relaxation with rounding, or Lagrangian relaxation:** relaxing the coverage constraints yields upper bounds, and Lagrangian relaxation fits the course's decomposition topic. Optional.

## Sensitivity analysis (spec section 9)
- **Budget *B*:** trace people covered against budget (a coverage curve). Find where returns diminish.
- **Radius *R*** (5, 10, 15 mi): how much does the coverage standard change the plan?
- **Cost ratio:** new grocer vs upgrade. When does funding a full grocer beat funding several upgrades?
- **Equity weight α** on low-income tracts: does the plan shift toward poorer places, and what does that cost in total coverage?
- **Distance type** (optional): straight-line vs driving. Do mountain roads change which sites are chosen? This ties back to question 2.
- **Robustness** (optional, stochastic): scenarios where existing full-service grocers close, which turns the problem into a two-stage or scenario-based stochastic program.

## Computational study (spec section 10)
- **Instance size:** one county → ARC Tennessee → one subregion → all of ARC Appalachia, measured by blocks and candidate sites.
- **Demand aggregation:** blocks vs block groups. Compare solve time and the error aggregation introduces.
- **Method:** MIP vs greedy (time, plus greedy's gap to the MIP optimum) and MCLP vs p-median (solvable size).
- **Results to report:** runtime, MIP gap, number of nodes, and the LP-relaxation bound.

## Results to show the decision maker
- A map and table of funded sites by county.
- People covered, broken out into low-income and all others.
- Cost per person covered.
- **Independent feasibility check:** recompute coverage and spending directly from the chosen sites and the distance data, without using the solver.

## Open decisions
- [ ] Find out what solver or modeling language IE 522 uses.
- [ ] Choose the main study area: all of rural ARC Appalachia, or ARC Tennessee for a local decision maker.
- [ ] Find cited cost figures, for example Healthy Food Financing Initiative grants, healthy corner-store conversion program costs, and rural grocery start-up cost studies.
- [ ] Decide whether to include new-grocer sites or only store upgrades.
- [ ] Decide on individual vs group work and register any group on Canvas.

## AI-use reminder
The report needs an AI use statement (5 points lost if it's missing). The data work and code in notes 01–03 were done with Claude. Check the course AI policy, and **write the formulation yourself**, since the spec requires "you formulate it yourself."
