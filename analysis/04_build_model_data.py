"""Build input files for a facility-location model (IE 522 project).

For each instance (study area) and coverage radius R, writes to data/model/<instance>/:
  demand_<level>_R<R>.csv  rural demand points more than R mi from a full-service grocer
                           (id, pop, low_income, county_fips, subregion, lat, lon)
  sites.csv                candidate sites (id, name, site_type, store_type, chain, county_fips, lat, lon)
  cover_<level>_R<R>.csv   pairs (demand_id, site_id, dist_mi) with dist_mi <= R

site_type:
  upgrade_grocery      independent Small/Medium Grocery Store (fresh-food upgrade candidate)
  upgrade_convenience  independent Convenience Store (fresh-food upgrade candidate)
  new_store            Census 2020 place (town or CDP) internal point (new grocer candidate)
  dollar               Dollar General / Family Dollar / Dollar Tree (comparison only; not
                       a realistic grant recipient)
chain = store name (digits/punctuation stripped) appears at >= CHAIN_MIN active SNAP stores
nationally. Chain grocers/convenience stores are excluded from the upgrade types.

level = "block" (2020 Census blocks) or "bg" (block groups; population-weighted centroids).
Distances are straight-line (great-circle) miles. Costs and the budget are NOT included:
they are set in the model notebook (see notes/06-cost-parameters.md).

Requires 03_store_type_access.py to have been run.
Run from the project root:  .venv/bin/python analysis/04_build_model_data.py
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("access", ROOT / "analysis" / "03_store_type_access.py")
access = importlib.util.module_from_spec(spec)
spec.loader.exec_module(access)

OUT = ROOT / "data" / "model"
RADII = [5, 10, 15]
CHAIN_MIN = 20
UPGRADE_TYPES = {"Small Grocery Store": "upgrade_grocery", "Medium Grocery Store": "upgrade_grocery",
                 "Convenience Store": "upgrade_convenience"}
INSTANCES = {  # name -> filter on block rows
    "tn": lambda b: b["county_fips"].str[:2] == "47",
    "central": lambda b: b["subregion"] == "Central",
    "south_central": lambda b: b["subregion"] == "South Central",
    "all": lambda b: pd.Series(True, index=b.index),
}
SITE_COLS = ["id", "name", "site_type", "store_type", "chain", "county_fips", "subregion", "lat", "lon"]


def chord(miles):
    return 2 * np.sin(miles / (2 * access.EARTH_MI))


def candidate_stores():
    stores = access.load_stores(access.SNAPSHOT)
    base = stores["Store Name"].str.upper().str.replace(r"[^A-Z ]", " ", regex=True).str.split().str.join(" ")
    stores["chain"] = base.map(base.value_counts()) >= CHAIN_MIN
    stores["site_type"] = np.where(stores["category"] == "dollar", "dollar",
                                   stores["Store Type"].map(UPGRADE_TYPES))
    keep = (stores["site_type"] == "dollar") | (stores["site_type"].notna() & ~stores["chain"])
    stores = stores[keep].rename(columns={"Record ID": "id", "Store Name": "name", "Store Type": "store_type"})
    stores["id"] = "S" + stores["id"].astype(str)
    return stores


def candidate_places():
    p = pd.read_csv(ROOT / "data" / "raw" / "places" / "2020_Gaz_place_national.txt", sep="\t", dtype={"GEOID": str})
    p.columns = p.columns.str.strip()
    return pd.DataFrame({"id": "P" + p["GEOID"], "name": p["NAME"] + ", " + p["USPS"], "site_type": "new_store",
                         "store_type": p["NAME"].str.extract(r"(CDP|city|town|village|borough)$")[0].fillna("place"),
                         "chain": False, "lat": p["INTPTLAT"], "lon": p["INTPTLONG"]})


def load_inputs():
    blocks = access.load_blocks()
    near = pd.read_csv(ROOT / "data" / "processed" / "appalachia_blocks_nearest_store.csv.gz",
                       dtype={"GEOID": str, "county_fips": str})
    blocks = blocks.merge(near[["GEOID", "rural", "LowIncomeTracts", "subregion", "d_full_service"]], on="GEOID")
    sites = pd.concat([candidate_stores(), candidate_places()], ignore_index=True)
    # Place each site in the county of its nearest populated ARC block (sites > 1 mi away are outside)
    tree = access.cKDTree(access.unit_xyz(blocks["lat"].to_numpy(), blocks["lon"].to_numpy()))
    d, idx = tree.query(access.unit_xyz(sites["lat"].to_numpy(), sites["lon"].to_numpy()))
    sites["county_fips"] = blocks["county_fips"].to_numpy()[idx]
    sites["subregion"] = blocks["subregion"].to_numpy()[idx]
    return blocks, sites.loc[d <= chord(1.0), SITE_COLS]


def demand_points(blocks, level):
    b = blocks.rename(columns={"GEOID": "id", "LowIncomeTracts": "low_income"})
    if level == "block":
        return b[["id", "pop", "low_income", "county_fips", "subregion", "lat", "lon", "d_full_service"]]
    b = b.assign(bg=b["id"].str[:12], wlat=b["lat"] * b["pop"], wlon=b["lon"] * b["pop"])
    g = b.groupby("bg").agg(pop=("pop", "sum"), low_income=("low_income", "first"),
                            county_fips=("county_fips", "first"), subregion=("subregion", "first"),
                            wlat=("wlat", "sum"), wlon=("wlon", "sum"), d_full_service=("d_full_service", "min"))
    g["lat"], g["lon"] = g["wlat"] / g["pop"], g["wlon"] / g["pop"]
    return g.reset_index().rename(columns={"bg": "id"})[
        ["id", "pop", "low_income", "county_fips", "subregion", "lat", "lon", "d_full_service"]]


def cover_pairs(dem, sites, radius):
    dxyz = access.unit_xyz(dem["lat"].to_numpy(), dem["lon"].to_numpy())
    sxyz = access.unit_xyz(sites["lat"].to_numpy(), sites["lon"].to_numpy())
    pairs = access.cKDTree(sxyz).query_ball_point(dxyz, chord(radius))
    di = np.repeat(np.arange(len(dem)), [len(p) for p in pairs])
    sj = np.concatenate([np.asarray(p, dtype=int) for p in pairs]) if len(di) else np.array([], int)
    dist = 2 * access.EARTH_MI * np.arcsin(np.clip(np.linalg.norm(dxyz[di] - sxyz[sj], axis=1) / 2, 0, 1))
    return pd.DataFrame({"demand_id": dem["id"].to_numpy()[di], "site_id": sites["id"].to_numpy()[sj],
                         "dist_mi": dist.round(3)})


def main():
    blocks, sites_all = load_inputs()
    rural = blocks[blocks["rural"]]
    summary = []
    for name, keep in INSTANCES.items():
        folder = OUT / name
        folder.mkdir(parents=True, exist_ok=True)
        area = rural[keep(rural)]
        sites = sites_all[sites_all["county_fips"].isin(set(area["county_fips"]))]
        sites.to_csv(folder / "sites.csv", index=False)
        types = sites.set_index("id")["site_type"]
        for level in ["block", "bg"]:
            for r in RADII:
                # A block counts as demand if it is more than R mi from a full-service grocer
                dem = demand_points(area[area["d_full_service"] > r], level)
                cov = cover_pairs(dem, sites, r)
                dem.drop(columns="d_full_service").to_csv(folder / f"demand_{level}_R{r}.csv", index=False)
                cov.to_csv(folder / f"cover_{level}_R{r}.csv", index=False)
                row = {"instance": name, "level": level, "R_mi": r, "demand_points": len(dem),
                       "demand_pop": int(dem["pop"].sum()), "cover_pairs": len(cov)}
                for t in ["upgrade_grocery", "upgrade_convenience", "new_store", "dollar"]:
                    c = cov[cov["site_id"].map(types) == t]
                    row[f"{t}_sites"] = c["site_id"].nunique()
                    row[f"{t}_coverable_pop"] = int(dem.loc[dem["id"].isin(c["demand_id"]), "pop"].sum())
                c = cov[cov["site_id"].map(types) != "dollar"]
                row["coverable_pop_excl_dollar"] = int(dem.loc[dem["id"].isin(c["demand_id"]), "pop"].sum())
                summary.append(row)
    s = pd.DataFrame(summary)
    s.to_csv(OUT / "instance_summary.csv", index=False)
    print(s[s["level"] == "block"].T.to_string())


if __name__ == "__main__":
    main()
