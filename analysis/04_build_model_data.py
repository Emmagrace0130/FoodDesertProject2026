"""Build input files for a facility-location model (IE 522 project).

For each instance (study area) and coverage radius R, writes to data/model/<instance>/:
  demand_<level>_R<R>.csv  rural demand points more than R mi from a full-service grocer
                           (id, pop, low_income, county_fips, subregion, lat, lon)
  sites.csv                candidate upgrade sites: SNAP dollar stores and small/medium
                           grocers in the area (id, name, category, store_type, county_fips, lat, lon)
  cover_<level>_R<R>.csv   pairs (demand_id, site_id, dist_mi) with dist_mi <= R

level = "block" (2020 Census blocks) or "bg" (block groups; population-weighted centroids).
Distances are straight-line (great-circle) miles. Costs and the budget are NOT included:
they must come from cited sources and are set in the model notebook.

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
UPGRADE_TYPES = {"Small Grocery Store", "Medium Grocery Store"}
INSTANCES = {  # name -> filter on block rows
    "tn": lambda b: b["county_fips"].str[:2] == "47",
    "central": lambda b: b["subregion"] == "Central",
    "south_central": lambda b: b["subregion"] == "South Central",
    "all": lambda b: pd.Series(True, index=b.index),
}


def chord(miles):
    return 2 * np.sin(miles / (2 * access.EARTH_MI))


def load_inputs():
    blocks = access.load_blocks()
    near = pd.read_csv(ROOT / "data" / "processed" / "appalachia_blocks_nearest_store.csv.gz",
                       dtype={"GEOID": str, "county_fips": str})
    blocks = blocks.merge(near[["GEOID", "rural", "LowIncomeTracts", "subregion", "d_full_service"]], on="GEOID")
    stores = access.load_stores(access.SNAPSHOT)
    stores = stores[(stores["category"] == "dollar") | stores["Store Type"].isin(UPGRADE_TYPES)].copy()
    # Place each store in the county of its nearest populated ARC block (stores > 1 mi away are outside)
    tree = access.cKDTree(access.unit_xyz(blocks["lat"].to_numpy(), blocks["lon"].to_numpy()))
    d, idx = tree.query(access.unit_xyz(stores["lat"].to_numpy(), stores["lon"].to_numpy()))
    stores["county_fips"] = blocks["county_fips"].to_numpy()[idx]
    stores["subregion"] = blocks["subregion"].to_numpy()[idx]
    stores = stores[d <= chord(1.0)]
    return blocks, stores


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
    blocks, stores = load_inputs()
    rural = blocks[blocks["rural"]]
    summary = []
    for name, keep in INSTANCES.items():
        folder = OUT / name
        folder.mkdir(parents=True, exist_ok=True)
        area = rural[keep(rural)]
        area_counties = set(area["county_fips"])
        sites = stores[stores["county_fips"].isin(area_counties)].rename(
            columns={"Record ID": "id", "Store Name": "name", "Store Type": "store_type"})
        sites = sites[["id", "name", "category", "store_type", "county_fips", "lat", "lon"]]
        sites.to_csv(folder / "sites.csv", index=False)
        for level in ["block", "bg"]:
            for r in RADII:
                # A block counts as demand if it is more than R mi from a full-service grocer
                dem = demand_points(area[area["d_full_service"] > r], level)
                cov = cover_pairs(dem, sites, r)
                dem.drop(columns="d_full_service").to_csv(folder / f"demand_{level}_R{r}.csv", index=False)
                cov.to_csv(folder / f"cover_{level}_R{r}.csv", index=False)
                coverable = dem["id"].isin(cov["demand_id"])
                summary.append({"instance": name, "level": level, "R_mi": r, "demand_points": len(dem),
                                "demand_pop": int(dem["pop"].sum()), "sites": len(sites),
                                "useful_sites": cov["site_id"].nunique(), "cover_pairs": len(cov),
                                "coverable_pop": int(dem.loc[coverable, "pop"].sum())})
    s = pd.DataFrame(summary)
    s.to_csv(OUT / "instance_summary.csv", index=False)
    print(s.to_string(index=False))


if __name__ == "__main__":
    main()
