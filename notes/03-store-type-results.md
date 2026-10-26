# Store-Type Results: Dollar Stores and Disappearing Food Deserts

*Oct 26, 2026. Scripts: `analysis/02_fetch_blocks.py` and `analysis/03_store_type_access.py`. Outputs: `data/processed/`.*

## Method
- **Stores:** USDA FNS Historical SNAP Retailer Locator data (2005–2025), limited to stores authorized on June 30, 2025, the same snapshot the SRAM uses. Farmers' markets and delivery routes are excluded, as in the SRAM.
- **Store categories**
  - **Full-service:** FNS types Supermarket, Super Store, and Large Grocery Store, which is close to the LRAM definition.
  - **Dollar:** Dollar General, Family Dollar, Dollar Tree, or DG Market, matched by store name. FNS files most of these under "Combination Grocery/Other."
  - **Other:** convenience stores, small and medium grocers, specialty stores, and the rest.
- **Population:** 640,627 populated 2020 Census blocks in the 423 ARC counties, located by the Census Bureau's interior point for each block (from TIGERweb). They total 26,135,136 people, which matches the SRAM exactly.
- **Distance:** great-circle (straight-line) distance from each block to the nearest store of each category nationwide, so stores just across the region's border count.
- **Flags:** USDA's rules. A tract is **low access** if at least 500 people or 33% of its residents live beyond the threshold (1 mile urban, 10 miles rural). It is a **food desert (LILA)** if it is also a low-income tract under the SRAM's flag. Rural/urban comes from the SRAM tract flag.
- **Validation:** using "any SNAP store," these flags reproduce the SRAM's straight-line results.
  - Tract flags agree for 97.3% of tracts: 1,058 low-access tracts here versus 1,113 in SRAM.
  - Low-access population correlates at r = 0.965 by tract.
  - The remaining gap likely comes from using block points instead of SRAM's 90 m population grid.

## Result 1: Store type, not time, erases rural food deserts
Same year (2025), same population, same distance method. Only the store definition changes:

| Rural Appalachia (3,663 tracts) | Full-service grocers only | Any SNAP store |
|---|---|---|
| Food-desert (LILA) tracts | **202** | **0** |
| Low-access tracts | 320 | 1 |
| People beyond 10 mi | 489,657 | 5,618 |

- **Store type explains the drop.** The SRAM shows zero rural food deserts because it counts dollar and convenience stores, not because supermarkets were added between 2019 and 2025.
- **Measured against full-service grocers, rural food deserts have not decreased.** The 2019 supermarket map (LRAM) showed 155 rural LILA tracts out of 2,888. This method finds 202 out of 3,663 in 2025. The two maps use different tract boundaries and rural definitions, so this comparison is suggestive, not exact.
- **Robustness check:** counting Medium Grocery Stores as full-service still leaves 155 rural LILA tracts and 374,472 people beyond 10 miles.

## Result 2: Dollar stores fill in for grocers in rural Appalachia
- **464,000 rural residents (3.6%)** live more than 10 miles from a full-service grocer but within 10 miles of a dollar store. These are the people the new map counts as having food access only because of a dollar store.
- **For 33% of rural residents, the nearest SNAP store is a dollar store.** For **77%**, a dollar store is closer than a full-service grocer.
- **Median distances for rural residents:** 3.6 mi to a full-service grocer, 2.0 mi to a dollar store, 1.4 mi to any SNAP store. The 90th percentile to a full-service grocer is 8.0 mi.
- **North Central Appalachia stands out:** 8.2% of its rural population lives beyond 10 miles from a full-service grocer, about double the other subregions.

**Counties where dollar stores account for the largest share of "access":**

| County | Beyond 1/10 mi from full-service | Beyond 1/10 mi from any store | Rescued by dollar store |
|---|---|---|---|
| Clay Co., WV | 81.5% | 0.0% | 80.2% |
| Bath Co., VA | 85.5% | 5.4% | 78.1% |
| Highland Co., VA | 91.9% | 5.3% | 76.8% |
| Robertson Co., KY | 73.4% | 0.0% | 73.4% |
| Forest Co., PA | 53.6% | 0.3% | 53.2% |
| Vinton Co., OH | 48.6% | 0.0% | 48.6% |
| Kemper Co., MS | 48.4% | 0.2% | 47.3% |

## Caveats
- **Store types come from FNS.** Some "Super Stores" may not be full grocers, and some good independent grocers are filed as Medium or Small Grocery. Spot-check the top counties, such as Clay Co., WV, by hand.
- **Interior points.** Block interior points are not where people actually live within a block, but rural blocks are small enough that the error should be minor.
- **Distance is straight-line only so far.** Driving distance, Q2, comes next.
- **Coordinates.** A small share of FNS coordinates may be ZIP-code or city centroids rather than exact store locations.
- **Physical access only.** Prices, stock, and quality are not measured. A dollar store "counting" as access says nothing about whether it sells fresh produce.

## Possible paper framing
> USDA's 2026 SNAP-authorized Retailer Access Map shows no low-income, low-access rural tracts in Appalachia. Holding year, population, and distance method constant, that disappearance is entirely due to counting dollar and convenience stores as food retailers: measured against full-service grocers, 202 rural Appalachian tracts remain food deserts, and 464,000 rural residents have food access on paper only because of a dollar store.

## Next steps
- [ ] Hand-check stores in about 5 top counties to confirm FNS store types. If possible, check whether dollar stores there sell fresh produce (some Dollar General locations do).
- [ ] Q2, driving distance: add road-network distances (for example with OSRM and OpenStreetMap data) to the full-service grocer and dollar-store measures, plus a terrain ruggedness index.
- [ ] Trends over time: count Appalachian dollar-store openings and full-service grocer closures from 2005 to 2025 using the same historical file.
- [ ] Bring the research question to an advisor or faculty member, for example in UTK Geography or Public Health, to assess fit.
