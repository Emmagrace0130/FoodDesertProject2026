"""Separate the store-type effect from the time effect (Q1).

For every populated 2020 Census block in ARC Appalachia, compute straight-line
distance to the nearest SNAP store of each type, using stores active on
2025-06-30 (same snapshot as SRAM). Then rebuild USDA-style low-access and
LILA flags with (a) full-service grocers only and (b) any SNAP store.

Inputs: data/raw/blocks/ (02_fetch_blocks.py), SNAP historical retailer file,
SRAM general tract file, ARC subregions.
Run from the project root:  .venv/bin/python analysis/03_store_type_access.py
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

warnings.simplefilter("ignore", pd.errors.PerformanceWarning)
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
SNAPSHOT = pd.Timestamp("2025-06-30")
EARTH_MI = 3958.8

FULL_SERVICE = {"Supermarket", "Super Store", "Large Grocery Store"}
EXCLUDED = {"Farmers' Market", "Delivery Route"}  # SRAM excludes these too
DOLLAR_RE = r"DOLLAR GENERAL|FAMILY DOLLAR|DOLLAR TREE|\bDG MARKET\b"


def load_stores(date):
    df = pd.read_csv(RAW / "snap_retailers" / "Historical SNAP Retailer Locator Data 2005-2025.csv",
                     dtype=str, encoding="utf-8-sig", encoding_errors="replace")
    auth = pd.to_datetime(df["Authorization Date"], errors="coerce")
    end = pd.to_datetime(df["End Date"].str.strip().replace("", None), errors="coerce")
    df = df[(auth <= date) & (end.isna() | (end > date)) & ~df["Store Type"].isin(EXCLUDED)].copy()
    df["lat"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["lon"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    dollar = df["Store Name"].str.upper().str.contains(DOLLAR_RE, regex=True, na=False)
    df["category"] = np.where(dollar, "dollar",
                     np.where(df["Store Type"].isin(FULL_SERVICE), "full_service", "other"))
    return df


def unit_xyz(lat, lon):
    lat, lon = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def nearest_miles(tree, pts):
    chord, _ = tree.query(pts)
    return 2 * EARTH_MI * np.arcsin(np.clip(chord / 2, 0, 1))


def load_blocks():
    files = sorted((RAW / "blocks").glob("*.csv"))
    b = pd.concat([pd.read_csv(f, dtype={"GEOID": str}) for f in files], ignore_index=True)
    b["tract"] = b["GEOID"].str[:11]
    b["county_fips"] = b["GEOID"].str[:5]
    return b.rename(columns={"POP100": "pop", "INTPTLAT": "lat", "INTPTLON": "lon"})


def flag_low_access(tract_df, beyond_col):
    """USDA rule: >=500 people or >=33% of tract beyond the threshold."""
    return (tract_df[beyond_col] >= 500) | (tract_df[beyond_col] / tract_df["pop"] >= 0.33)


def main():
    arc = pd.read_excel(RAW / "arc" / "subregions2021.xlsx", header=4, dtype=str).dropna(subset=["FIPS"])
    arc = arc.assign(county_fips=arc["FIPS"].str.zfill(5))[["county_fips", "SUBREGION"]].rename(
        columns={"SUBREGION": "subregion"})
    gen = pd.read_csv(RAW / "sram" / "SRAM General Tract Characteristics Data.csv",
                      dtype={"CensusTract20": str}, encoding="latin-1")
    gen["tract"] = gen["CensusTract20"].str.zfill(11)

    blocks = load_blocks().merge(arc, on="county_fips").merge(
        gen[["tract", "Urban", "LowIncomeTracts", "State", "County20"]], on="tract", how="left")
    print(f"blocks: {len(blocks):,}  population: {blocks['pop'].sum():,}  "
          f"(SRAM ARC total 26,135,136)  missing tract match: {blocks['Urban'].isna().sum()}")

    stores = load_stores(SNAPSHOT)
    print("\nActive SNAP stores 2025-06-30 (US):", stores["category"].value_counts().to_dict())
    pts = unit_xyz(blocks["lat"].to_numpy(), blocks["lon"].to_numpy())
    for cat in ["full_service", "dollar", "other"]:
        s = stores[stores["category"] == cat]
        blocks[f"d_{cat}"] = nearest_miles(cKDTree(unit_xyz(s["lat"], s["lon"])), pts)
    blocks["d_any"] = blocks[["d_full_service", "d_dollar", "d_other"]].min(axis=1)
    blocks["d_nonfull"] = blocks[["d_dollar", "d_other"]].min(axis=1)
    blocks["nearest_is"] = blocks[["d_full_service", "d_dollar", "d_other"]].idxmin(axis=1).str[2:]
    blocks["rural"] = blocks["Urban"] == 0
    blocks["thresh"] = np.where(blocks["rural"], 10.0, 1.0)
    for cat in ["full_service", "any"]:
        blocks[f"beyond_{cat}"] = blocks["pop"] * (blocks[f"d_{cat}"] > blocks["thresh"])
    blocks["beyond10_full_service"] = blocks["pop"] * (blocks["d_full_service"] > 10)
    blocks["beyond20_full_service"] = blocks["pop"] * (blocks["d_full_service"] > 20)
    blocks["beyond10_any"] = blocks["pop"] * (blocks["d_any"] > 10)
    # "Rescued": far from a full-service grocer, but within threshold of a dollar store
    blocks["rescued_by_dollar"] = blocks["pop"] * (
        (blocks["d_full_service"] > blocks["thresh"]) & (blocks["d_dollar"] <= blocks["thresh"]))
    blocks.drop(columns=["lat", "lon"]).to_csv(OUT / "appalachia_blocks_nearest_store.csv.gz", index=False)

    # --- Tract-level USDA-style flags, 2025 stores, holding everything but store type fixed ---
    t = blocks.groupby("tract").agg(
        pop=("pop", "sum"), rural=("rural", "first"), low_income=("LowIncomeTracts", "first"),
        subregion=("subregion", "first"), beyond_full_service=("beyond_full_service", "sum"),
        beyond_any=("beyond_any", "sum"), rescued=("rescued_by_dollar", "sum"))
    t["LA_full_service"] = flag_low_access(t, "beyond_full_service")
    t["LA_any"] = flag_low_access(t, "beyond_any")
    t["LILA_full_service"] = t["LA_full_service"] & (t["low_income"] == 1)
    t["LILA_any"] = t["LA_any"] & (t["low_income"] == 1)
    t.to_csv(OUT / "appalachia_tracts_store_type.csv")

    print("\n=== Tracts, 2025 stores, straight-line, 1 mi urban / 10 mi rural ===")
    rows = []
    for (sub, rural), g in t.groupby(["subregion", "rural"]):
        rows.append({"subregion": sub, "area": "rural" if rural else "urban", "tracts": len(g),
                     "LILA_full_service": int(g["LILA_full_service"].sum()), "LILA_any": int(g["LILA_any"].sum()),
                     "LA_full_service": int(g["LA_full_service"].sum()), "LA_any": int(g["LA_any"].sum()),
                     "pop_beyond_full_service": int(g["beyond_full_service"].sum()),
                     "pop_beyond_any": int(g["beyond_any"].sum()),
                     "pop_rescued_by_dollar": int(g["rescued"].sum())})
    tr = pd.DataFrame(rows)
    tot = tr.groupby("area").sum(numeric_only=True).reset_index().assign(subregion="ALL")
    tr = pd.concat([tr, tot], ignore_index=True)
    tr.to_csv(OUT / "store_type_tract_flags.csv", index=False)
    print(tr.to_string(index=False))

    # --- Rural people: distances and what their nearest store is ---
    r = blocks[blocks["rural"]]

    def wq(g, col, q):
        o = g.sort_values(col)
        c = o["pop"].cumsum()
        return o[col].to_numpy()[np.searchsorted(c, q * c.iloc[-1])]

    rows = []
    for sub, g in [("ALL rural Appalachia", r)] + list(r.groupby("subregion")):
        p = g["pop"].sum()
        rows.append({
            "group": sub, "rural_pop": p,
            "median_mi_full_service": wq(g, "d_full_service", .5),
            "p90_mi_full_service": wq(g, "d_full_service", .9),
            "median_mi_dollar": wq(g, "d_dollar", .5),
            "median_mi_any": wq(g, "d_any", .5),
            "pct_beyond10_full_service": 100 * g["beyond10_full_service"].sum() / p,
            "pct_beyond20_full_service": 100 * g["beyond20_full_service"].sum() / p,
            "pct_beyond10_any": 100 * g["beyond10_any"].sum() / p,
            "pct_nearest_is_dollar": 100 * g.loc[g["nearest_is"] == "dollar", "pop"].sum() / p,
            "pct_dollar_closer_than_full": 100 * g.loc[g["d_dollar"] < g["d_full_service"], "pop"].sum() / p,
            "pct_rescued_by_dollar": 100 * g["rescued_by_dollar"].sum() / p,
        })
    rd = pd.DataFrame(rows)
    rd.to_csv(OUT / "rural_distance_by_store_type.csv", index=False)
    print("\n=== Rural Appalachia: distance to nearest store by type (straight-line miles) ===")
    print(rd.round(2).to_string(index=False))

    # --- Validation against USDA SRAM straight-line numbers ---
    sd = pd.read_csv(RAW / "sram" / "SRAM Straight Line Distance Data.csv",
                     dtype={"CensusTract20": str}, encoding="latin-1")
    sd["tract"] = sd["CensusTract20"].str.zfill(11)
    v = t.join(sd.set_index("tract")[["SD_SRAM_LAPOP1_10", "SD_SRAM_LA1and10"]], how="left")
    print(f"\nValidation (ARC tracts): our any-store LA pop {v['beyond_any'].sum():,.0f} vs SRAM "
          f"{v['SD_SRAM_LAPOP1_10'].sum():,.0f}; LA tracts {int(v['LA_any'].sum())} vs SRAM "
          f"{int(v['SD_SRAM_LA1and10'].sum())}; tract-flag agreement "
          f"{100 * (v['LA_any'] == (v['SD_SRAM_LA1and10'] == 1)).mean():.1f}%; "
          f"corr of LA pop {v['beyond_any'].corr(v['SD_SRAM_LAPOP1_10']):.3f}")

    # --- County table ---
    c = blocks.groupby("county_fips").agg(
        state=("State", "first"), county=("County20", "first"), subregion=("subregion", "first"),
        pop=("pop", "sum"), rural_pop=("pop", lambda s: s[blocks.loc[s.index, "rural"]].sum()),
        beyond_full_service=("beyond_full_service", "sum"), beyond_any=("beyond_any", "sum"),
        rescued=("rescued_by_dollar", "sum"))
    for k in ["beyond_full_service", "beyond_any", "rescued"]:
        c[f"pct_{k}"] = 100 * c[k] / c["pop"]
    c["pct_rural"] = 100 * c["rural_pop"] / c["pop"]
    c.to_csv(OUT / "county_store_type_access.csv")
    cols = ["state", "county", "subregion", "pct_rural", "pct_beyond_full_service", "pct_beyond_any", "pct_rescued"]
    print("\n=== Counties where dollar stores 'rescue' the largest share of residents ===")
    print(c.sort_values("pct_rescued", ascending=False)[cols].head(20).round(1).to_string())


if __name__ == "__main__":
    main()
