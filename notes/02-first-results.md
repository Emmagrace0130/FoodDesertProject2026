# First Results: Old vs New USDA Food-Access Maps in Appalachia

*Oct 26, 2026. Script: `analysis/01_compare_maps.py`. Outputs: `data/processed/`. Raw data (not in git) is in `data/raw/`.*

## Data
- **LRAM 2019** (the old Food Access Research Atlas, FARA): counts only supermarkets, supercenters, and large grocers. Uses straight-line distance, 2010 census tracts and population, and 2019 store locations.
- **SRAM 2025**: counts every store authorized to accept SNAP, including dollar and convenience stores. Uses both straight-line and driving distance, 2020 tracts and population, and June 2025 store locations.
- **ARC Subregions 2021**: all 423 Appalachian counties, each labeled with a subregion (Northern, North Central, Central, South Central, or Southern). All 423 matched in both maps.
- **Thresholds:** unless noted, "low access" (LA) means living more than 1 mile from a store in urban areas or more than 10 miles in rural areas. LILA means a tract that is both low income and low access, which is USDA's working definition of a food desert.

## Q1: Do food deserts disappear on paper when every SNAP store counts?
**In rural Appalachia, they essentially do.**

| Rural Appalachia (each map's own rural tracts) | LRAM 2019 supermarkets, straight-line | SRAM 2025 all SNAP stores, straight-line | SRAM 2025, driving |
|---|---|---|---|
| Low-access tracts | 256 | 2 | 49 |
| Food-desert (LILA) tracts | 155 | **0** | 29 |
| People low access | 394,935 (3.2%) | 8,823 (0.1%) | 114,428 (0.9%) |

- Under the new map's straight-line measure, no rural Appalachian tract counts as a food desert. Nearly everyone lives within 10 miles of *some* SNAP store.
- **Big drops by county**
  - Highland Co., VA went from 99.7% low access to 7.5%.
  - Gilmer Co., WV went from 81.6% to 0%.
  - Robertson Co., KY went from 74.8% to 0%.
  - Sequatchie Co., TN went from 42.1% to 0%.
- **Why it matters:** the 10-mile rural cutoff was designed for supermarkets. Applying it to any SNAP store, including a dollar or convenience store, sets a very low bar.

**What this comparison can't separate yet:**
- **Store type versus time.** Between the two maps, store types *and* the years changed: 2019 to 2025 stores, and 2010 to 2020 population. The new map has no supermarket-only version, so this comparison can't show how much of the drop comes from dollar and convenience stores versus new supermarkets.
- **Rural and urban labels changed.** Appalachia has 2,888 rural tracts in the old map and 3,668 in the new one, so some tracts switched between the 1-mile and 10-mile rules. Example: Grainger Co., TN went *up* from 0% to 11%.
- **The cleaner design:** use USDA's SNAP Retailer historical data, which lists each store's type and coordinates. With it we can compute distance to the nearest *supermarket* and to the nearest *dollar or convenience store* using the same 2025 stores and population.

## Q2: Do mountains distort straight-line measures?
**Driving distance matters more in Appalachia at the 10-mile rural scale. At 1 mile, the difference is about the same as elsewhere.**

Rural population living more than 10 miles from any SNAP store:

| Group | Straight-line | Driving | Ratio |
|---|---|---|---|
| Rest of rural US | 1.50% | 3.37% | 2.2x |
| Central Appalachia | 0.01% (173 people) | 1.38% (20,586 people) | ~119x |
| South Central | 0.08% | 1.20% | 15x |
| Southern | 0.06% | 0.76% | 13x |
| North Central | 0.12% | 1.22% | 10x |
| Northern | 0.07% | 0.45% | 6x |

- **The mountain pattern is clear.** Central Appalachia, the most rugged subregion, shows the largest gap, and Northern shows the smallest. The absolute numbers are small, though, because nearly everyone lives within 10 miles of some store.
- **Food deserts reappear with driving distance.** Under driving distance, 29 rural Appalachian tracts count as food deserts, compared with 0 under straight-line distance.
- **Tennessee examples:** Hancock Co. rose from 0% to 10.6% low access, Clay Co. from 0% to 9.0%, and Jackson Co. from 0% to 5.9%.
- **At 1 mile, the effect is not specific to Appalachia.** Driving adds about 13 to 16 points in Appalachia and about 12 points elsewhere.
- **Suburbs lead the county rankings.** The counties with the largest increases from switching to driving distance are suburban, for example Gwinnett and Forsyth in Georgia and Knox in Tennessee. Winding cul-de-sac road layouts likely cause this. Keep Q2 focused on rural tracts.
- **Limitation:** subregion is only a rough stand-in for terrain. A real test needs a ruggedness measure for each tract or county, such as a terrain ruggedness index calculated from elevation data.

## Possible research question
> USDA's new food-access measure counts every SNAP store and drops essentially all rural Appalachian food deserts. How much of that change comes from dollar and convenience stores, and how much more access does mountain terrain hide when distance is measured in a straight line?

## Next steps
- [ ] Download the USDA SNAP Retailer Locator historical data, which has store type and coordinates. Rebuild access for supermarkets only versus dollar and convenience stores only, using 2025 stores.
- [ ] Add a terrain ruggedness measure, such as a tract- or county-level index from USGS elevation data. Test whether the gap between driving and straight-line distance increases with ruggedness.
- [ ] Use the 2020 Census tract-relationship file to compare the same areas across both maps.
- [ ] Look into whether any paper already uses the SRAM, to confirm the gap is still open.
