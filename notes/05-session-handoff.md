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
  - `sites.csv`: candidate upgrade sites, meaning dollar stores and small or medium grocers
  - `demand_<block|bg>_R<5|10|15>.csv`: rural demand points more than R miles from a full-service grocer
  - `cover_<block|bg>_R<R>.csv`: pairs (demand_id, site_id, dist_mi) with distance ≤ R
  - `data/model/instance_summary.csv`: sizes of every instance
- **Key sizes:**
  - TN, R=10: 1,930 blocks, 41k people, 252 useful sites
  - All, R=10: 25,015 blocks, 490k people, 2,212 sites
  - All, R=5: 166k blocks, 4.2M people
- **Drop R=15.** Almost no demand is left at that radius. Use R = 5 and 10, and maybe add 7.5.
- **Distances are straight-line.** Driving distance is an optional extension.

## To-do list
- [ ] **Gurobi license on this Mac.** Nothing is installed yet: no `gurobi.lic`, so it runs in size-limited mode. Run `grbgetkey <key>` while on the UT network or VPN, or use a Web License Service (WLS) `gurobi.lic` file, and save it as `~/gurobi.lic`. Test it with the 3,000-variable command in the next section.
- [ ] **Find cited costs:** what a store fresh-produce upgrade costs vs a new rural grocery store, plus a realistic budget. Possible sources: the Healthy Food Financing Initiative, healthy corner-store programs, rural grocery start-up studies.
- [ ] **Decide the scope:** store upgrades only, or upgrades plus new-grocer sites. Main study area: all of Appalachia, or Tennessee.
- [ ] **Write the formulation yourself**, as the spec requires. Then Claude can review it and help with experiment loops.
- [ ] **Sensitivity analysis:** budget, radius R, cost ratio, low-income weight; optionally driving distance and grocer-closure scenarios.
- [ ] **Computational study:** compare instance sizes (Tennessee up to all of Appalachia), blocks vs block groups, and the exact MIP vs a greedy heuristic (and optionally p-median).
- [ ] **AI use statement:** check the course AI policy. Claude did the data work and code in notes 01–03 and the model-data pipeline.
- [ ] **Commit to git.** Nothing is committed yet.
- [ ] **Research side, optional:** spot-check store types in Clay Co. WV and other top counties; robustness checks on how Appalachia is defined; dollar-store openings vs grocery closures from 2005 to 2025.

## Quick test that the Gurobi license works
Should print `2`, meaning optimal:
```
.venv/bin/python -c "import gurobipy as gp; m=gp.Model(); x=m.addVars(3000); m.optimize(); print(m.Status)"
```
