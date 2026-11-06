# IISE 2027 Abstract Draft

*Nov 6, 2026. Deadline **Nov 8, 2026**, submitted at https://www.iise.org/Annual/. Limit: 250 words. Current draft: 241 words. Conference: May 22–25, 2027, Louisville, KY.*

**Title:** Dollar Stores, Disappearing Food Deserts, and Optimal Fresh-Food Investment in Rural Appalachia

**Suggested track:** Operations Research (facility location). Alternatives: Health Systems, or Logistics & Supply Chain.

## Abstract

USDA's 2026 SNAP-authorized Retailer Access Map counts every SNAP-authorized store, including dollar and convenience stores, as a food retailer. Under this measure, low-income, low-access rural tracts in the 423-county Appalachian Regional Commission region fall to zero. Using 2025 USDA retailer records and 2020 Census block populations, we show that this change is driven by how stores are defined, not by new grocers: measured against full-service grocers alone, 202 rural Appalachian tracts remain food deserts, and about 464,000 rural residents have food access on paper only because of a dollar store. We then formulate a budgeted maximal covering location problem for a funder choosing between low-cost fresh-produce upgrades at independent stores (about $25,000 each) and new full-service grocery stores (about $1 million each), maximizing the rural population within R miles of a funded site. Candidate sites are independent grocers and convenience stores from USDA data and Census town centers; costs come from state and federal healthy food financing programs. For Appalachian Tennessee, Gurobi solves each instance to optimality in under one second. Under a 10-mile standard, about $1 million in upgrades covers 97% of rural residents who live beyond 10 miles of a grocer, while under a 5-mile standard, $3 million covers only 71%. Sensitivity analysis over budget, coverage radius, and costs shows that upgrades dominate new stores across the cited cost ranges. We discuss implications for how food access is measured and funded, and extensions to region-wide instances and quality-weighted coverage.

## Sources for each number
| Claim | Source |
|---|---|
| 202 rural food-desert tracts; 464,000 residents with access only because of a dollar store | notes/03-store-type-results.md |
| Under 1 s; 97% at $1M, R = 10 | notebook section 6.1, `results/budget_sweep_tn_block.csv` |
| 71% at $3M, R = 5 | same |
| Upgrades dominate new stores across the cited cost range | notebook section 6.2, `results/cost_sensitivity_tn_block.csv` |
