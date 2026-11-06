# Session Handoff: Start Here Next Time

*Last updated Oct 27, 2026. Read this file first in the next session.*

## Where things stand
**Research project:** food deserts in rural Appalachia. USDA's new 2026 food-access map (SRAM) counts dollar stores as food retailers, and that alone erases every rural food desert in Appalachia.
- Counting full-service grocers only: **202** rural food-desert tracts. Counting any SNAP store: **0**.
- **464,000** rural residents have "access" on paper only because a dollar store is nearby.
- For a third of rural residents, the nearest SNAP store is a dollar store.
- Details are in notes 01–03.

**IE 522 final project (due Wed Dec 9, 11:59 PM, Option 1 for extra credit):** a budgeted maximal covering location problem. Choose which stores to fund for fresh-produce upgrades, and possibly new grocers, to cover the most rural people within R miles. Solver: **Gurobi** (course standard). Full plan: [04-optimization-project-plan.md](04-optimization-project-plan.md).

## Files
| File | What it is |
|---|---|
| `notes/01-literature-scan.md` | Literature review and research gaps |
| `notes/02-first-results.md` | Old vs new USDA map comparison; straight-line vs driving distance |
| `notes/03-store-type-results.md` | Main dollar-store finding, methods, caveats |
| `notes/04-optimization-project-plan.md` | IE 522 plan: model, approaches, sensitivity, computational study |
| `analysis/01_compare_maps.py` | Old vs new map comparison |
| `analysis/02_fetch_blocks.py` | Downloads 2020 Census block points (TIGERweb) |
| `analysis/03_store_type_access.py` | Distance from each block to the nearest store by type |
| `analysis/04_build_model_data.py` | Builds the optimization model inputs in `data/model/` |
| `[DRAFT] IE522_Fa26_Final_project.pdf` | Course project specification |

**Rebuild everything from the project root, in order:**
```
.venv/bin/python analysis/01_compare_maps.py
.venv/bin/python analysis/02_fetch_blocks.py
.venv/bin/python analysis/03_store_type_access.py
.venv/bin/python analysis/04_build_model_data.py
```
- Raw data, in `data/raw/` and git-ignored, comes from USDA ERS (SRAM and LRAM), USDA FNS (historical SNAP retailers), ARC (county subregions), and the Census (TIGERweb blocks).
- The Python environment is `.venv/`, with pandas, scipy, gurobipy, and pypdf installed.

## Model inputs (`data/model/<instance>/`)
- **Instances:** `tn` (Appalachian Tennessee), `central`, `south_central`, `all`
- **Files**
  - `sites.csv`: candidate sites, with a `site_type` column: `upgrade_grocery`, `upgrade_convenience`, `new_store` (town centers), or `dollar` (comparison only)
  - `demand_<block|bg>_R<5|10|15>.csv`: rural demand points more than R miles from a full-service grocer
  - `cover_<block|bg>_R<R>.csv`: pairs (demand_id, site_id, dist_mi) with distance ≤ R
  - `data/model/instance_summary.csv`: sizes of every instance
- **Key sizes** (see `instance_summary.csv`):
  - TN, R=10: 1,930 blocks, 41k people. Useful sites: 21 independent grocers, 303 independent convenience stores, 100 towns.
  - All, R=10: 25,015 blocks, 490k people. Useful sites: 244 grocers, 2,293 convenience stores, 1,686 towns. 98% of people can be reached without using dollar stores.
  - All, R=5: 166k blocks, 4.2M people.
- **Drop R=15.** Almost no demand is left at that radius. Use R = 5 and 10, and maybe add 7.5.
- **Distances are straight-line.** Driving distance is an optional extension.

## To-do list
- [x] **Gurobi license on this Mac.** Done Oct 27: academic license 2854889, saved at `~/gurobi.lic`, expires 2027-08-20. The 3,000-variable test solved to optimal.
- [x] **Find cited costs.** Done, see [06-cost-parameters.md](06-cost-parameters.md). Base values: $25k per upgrade, $1M per new store, $3M budget.
- [x] **Decide the candidate sites.** Done Oct 27, and the data is rebuilt. Upgrades go to **independent** small or medium grocers (`upgrade_grocery`) and independent convenience stores (`upgrade_convenience`). New stores go at **town centers**, meaning Census 2020 place internal points for towns and CDPs (`new_store`). Dollar stores are kept as `dollar` for comparison only. A store counts as a chain when its name appears at 20 or more SNAP stores nationally.
- [ ] **Decide the scope:** store upgrades only, or upgrades plus new-grocer sites. Main study area: all of Appalachia, or Tennessee.
- [x] **Formulation.** Done Oct 28, see [07-formulation-worksheet.md](07-formulation-worksheet.md). Emma wrote the sets, parameters, variables, and objective; Claude completed the constraints and analysis with reported instructor permission. Disclose this in the AI statement.
- [x] **Base model coded and solved.** `notebooks/ie522_model.ipynb`, written by Claude. TN, R=10, $3M: optimal in 0.02 s. Funds 42 sites (38 convenience upgrades, 2 grocery upgrades, 2 new stores) and covers 40,478 of 41,397 people (97.8%; 40,599 is the maximum possible). All 5 sanity tests pass. **$3M is nearly enough to saturate TN**, so the interesting budget range is smaller; consider R=5 or the full region as the main case.
- [ ] **Sensitivity analysis:** budget, radius R, cost ratio, low-income weight; optionally driving distance and grocer-closure scenarios.
  - [x] **Budget sweep** (notebook section 6.1), TN blocks, $0–$5M, R = 5 and R = 10. Output: `results/budget_sweep_tn_block.csv`, `figures/fig_budget_curve_tn.png`, `figures/fig_site_mix_tn.png`.
    - **R = 10:** $500k covers 91%, $1M covers 97%, then coverage flattens. 47 upgrades reach everyone an upgrade can reach. Beyond that, each $1M new store adds only about 60–120 people.
    - **R = 5:** coverage climbs steadily: 41% at $1M, 71% at $3M, 80% at $5M. Only upgrades are funded at every budget.
    - Every solve is optimal in under 0.05 s.
  - [x] **Cost sensitivity** (section 6.2): upgrade cost $5k–$1M × new-store cost $0.8M/$1M/$2.1M, with budgets fixed at $1M (R=10) and $3M (R=5). Output: `results/cost_sensitivity_tn_block.csv`, `figures/fig_cost_sensitivity_tn.png`.
    - **R = 10, $1M budget:** coverage stays at 91–98% for upgrade costs up to $50k and drops to 75% at $90k.
    - **R = 5, $3M budget:** coverage falls from 82% at $5k to 36% at $90k, so it is much more cost-sensitive.
    - **New-store cost doesn't matter.** The model funds a new store only with money left over after upgrades run out, *even when an upgrade costs as much as a new store* ($1M).
    - **Modeling issue this exposed:** the model counts an upgraded convenience store as equal to a full grocery store. Proposed fix: a quality weight θ < 1 on upgrade coverage (two coverage levels). Decide with Emma.
  - [ ] Low-income weight α, quality weight θ (if adopted), and possibly the larger instances (all of Appalachia).
- [ ] **Computational study:** compare instance sizes (Tennessee up to all of Appalachia), blocks vs block groups, and the exact MIP vs a greedy heuristic (and optionally p-median).
- [ ] **AI use statement:** check the course AI policy. Claude did the data work and code in notes 01–03 and the model-data pipeline.
- [ ] **Commit to git.** Nothing is committed yet.
- [ ] **Research side, optional:** spot-check store types in Clay Co. WV and other top counties; robustness checks on how Appalachia is defined; dollar-store openings vs grocery closures from 2005 to 2025.

## Quick test that the Gurobi license works
Should print `2`, meaning optimal:
```
.venv/bin/python -c "import gurobipy as gp; m=gp.Model(); x=m.addVars(3000); m.optimize(); print(m.Status)"
```
