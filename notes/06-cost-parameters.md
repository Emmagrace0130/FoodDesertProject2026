# Cost Parameters for the IE 522 Model

*Oct 27, 2026. A web scan for cited figures. Open each source and confirm the numbers before citing them in the report.*

## Suggested values
| Parameter | Base value | Sensitivity range | Basis |
|---|---|---|---|
| **c_upgrade:** add fresh-produce refrigeration and display to an existing small store | **$25,000** | $5,000 – $90,000 | California CDFA Healthy Refrigeration Grant Program (2023): $4,058,760 to reach about 168 stores, roughly $24k per store, with individual awards of about $10k–$88k. Toledo caps awards at $20k. North Carolina's pilot caps them at $5k. |
| **c_new:** open a new small rural full-service grocery store | **$1,000,000** | $0.8M – $2.1M | Kansas community grocery stores: Axtell (2023, 7,600 sq ft) cost $791,568, and Grand Avenue Market in Plains (2021, 9,300 sq ft) cost $2.073M. |
| **B:** program budget | **$3,000,000** | $0.25M – $10M | HFFI FARE Fund: Round 1 (2025) awarded $3M to 14 projects, and the full 2024–25 cycle awarded $16.5M to 62 projects. HFFI partnership grants run $200k–$3M. North Carolina's pilot was $250k in total. |

- **Cost ratio:** at the base values, a new store costs about **40 times** an upgrade. One new grocery store costs as much as about 40 upgrades.
- **The base budget of $3M** buys about 120 upgrades, or 3 new stores, or a mix of the two.
- **Geography caveat:** the new-store costs are from Kansas. No Appalachian new-store cost turned up. State this as an assumption, and test the full range in the sensitivity analysis.

## Sources
**Store upgrades**
- [CDFA 2024 Healthy Refrigeration Grant Program legislative report](https://cafarmtofork.cdfa.ca.gov/docs/2024_CDFA_Healthy_Refrigeration_Legislative_Report.pdf)
- [CDFA 2023 HRGP awardees](https://cafarmtofork.cdfa.ca.gov/docs/hrgp/2023_HRGP_Awardees.pdf)
- [CDFA refrigeration program flyer](https://cafarmtofork.cdfa.ca.gov/docs/RefrigerationFlyer.pdf)
- [Civil Eats: California boosts corner stores (2022)](https://civileats.com/2022/02/22/california-gives-a-big-boost-to-corner-stores-that-sell-fresh-produce/)
- [City of Toledo Healthy Corner Store Initiative (2024)](https://toledo.oh.gov/news/2024/06/27/new-healthy-corner-store-initiative-accepting-applications-now)
- [Carolina Political Review: NC Healthy Food Small Retailer Program](https://www.carolinapoliticalreview.org/editorial-content/2019/1/22/general-assembly-must-reconsider-corner-store-initiative)

**New grocery stores**
- [IFF: Axtell, KS community grocery](https://iff.org/rural-kansas-community-bands-together-to-open-locally-owned-grocery-store/)
- [IFF: Grand Avenue Market, Plains, KS](https://iff.org/grand-avenue-market-a-20-year-quest-to-re-establish-a-local-grocery-store-in-rural-kansas/)
- [KCUR: Kansas rural grocery stores (2025)](https://www.kcur.org/housing-development-section/2025-09-28/rural-kansas-grocery-stores-closure-rural-healthy-foods-initiative)
- [HPPR: Plains nonprofit grocery closing (2026)](https://www.hppr.org/hppr-news/2026-03-24/a-rural-nonprofit-grocery-store-is-closing-in-kansas-showing-how-hard-it-is-to-fight-food-deserts). Shows that new stores can fail, a useful limitation and a possible scenario-based stochastic extension.
- [Kansas Reflector: states invest to save rural grocers (2024)](https://kansasreflector.com/2024/03/03/the-lifeblood-of-the-community-states-invest-to-save-rural-grocery-stores/)

**Budgets**
- [Reinvestment Fund: HFFI 2024–25 cycle, $16.5M to 62 projects](https://www.reinvestment.com/insights/healthy-food-financing-initiative-completes-2024-25-funding-cycle-with-16-5-million-to-promote-food-access-nationwide/)
- [Reinvestment Fund: FARE Round 1, about $3M](https://www.reinvestment.com/insights/healthy-food-financing-initiative-awards-nearly-3-million-through-food-access-and-retail-expansion-fare-fund/)
- [Reinvestment Fund: $20M partnerships program, $200k–$3M awards](https://www.reinvestment.com/insights/healthy-food-financing-initiative-announces-20-million-local-and-regional-healthy-food-financing-partnerships-grant-program/)
- [FARE Fund Round 1 award book](https://www.investinginfood.com/wp-content/uploads/2026/04/FARE_Fund_R1_AwardBook_FINAL.pdf)

**Appalachian context**
- [USDA RD: $351k in WV rural business development, including a $50k grocery feasibility study for **Clay County, WV**](https://www.rd.usda.gov/newsroom/news-release/usda-rural-development-announces-351000-investment-rural-business-development-west-virginia). Clay County is the top county in our dollar-store analysis.
- [USDA RD: $1.6M for healthy food access in WV (HFFI awards: $125k for H.U. Market, Bluefield; $184k for Mountain Farm Community Grocery, Kimball)](https://www.rd.usda.gov/newsroom/news-release/rural-development-invests-16-million-increase-access-healthy-foods-west-virginia)

**Dollar General produce rollout**
- [Grocery Dive: DG slowing produce rollout, about 7,000 stores with produce in 2025](https://www.grocerydive.com/news/dollar-general-third-quarter-earnings-produce-remodels/734840/)
- [Progressive Grocer: DG adding produce to 10,000 stores](https://progressivegrocer.com/dollar-general-adding-produce-10000-stores)

## Modeling issues the research raised
1. **Grant programs fund independent stores, not chains.** Healthy corner-store and refrigeration grants go to small independent retailers. A public funder paying to upgrade a Dollar General is not realistic. Make the **candidate upgrade sites independent small stores**: the Small and Medium Grocery Store types already in `sites.csv`, and possibly independent convenience stores. Chain dollar stores then stay part of the *story* (they are why the map looks fine) rather than being *decision variables*.
2. **About 7,000 Dollar General stores already sell some produce.** The SNAP data does not say which ones, which is another reason not to model dollar stores as upgrade sites.
3. **New stores can fail.** The Plains, Kansas store is closing. This could become a stochastic extension, with scenarios in which funded stores fail, or a stated limitation.
