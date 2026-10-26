"""First-pass comparison of USDA food-access maps for ARC Appalachian counties.

Q1: How does counting every SNAP store (SRAM 2025) instead of only supermarkets
    (LRAM 2019) change who is "low access"?  Both use straight-line distance here.
Q2: Within SRAM, how much does driving distance change things vs straight-line?

Run from the project root:  .venv/bin/python analysis/01_compare_maps.py
"""
import warnings
from pathlib import Path

import pandas as pd

warnings.simplefilter("ignore", pd.errors.PerformanceWarning)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Bedford city, VA (51515) merged into Bedford County (51019) in 2013.
FIPS_FIXES = {"51515": "51019"}


def load_arc():
    arc = pd.read_excel(RAW / "arc" / "subregions2021.xlsx", header=4, dtype=str)
    arc = arc.dropna(subset=["FIPS"])
    arc["FIPS"] = arc["FIPS"].str.zfill(5)
    return arc.rename(columns={"FIPS": "county_fips", "SUBREGION": "subregion"})[
        ["county_fips", "subregion"]
    ]


def load_tracts(path, tract_col):
    df = pd.read_csv(path, dtype={tract_col: str}, low_memory=False, encoding="latin-1")
    df["tract"] = df[tract_col].str.zfill(11)
    df["county_fips"] = df["tract"].str[:5].replace(FIPS_FIXES)
    return df


def load_sram():
    gen = load_tracts(RAW / "sram" / "SRAM General Tract Characteristics Data.csv", "CensusTract20")
    sd = load_tracts(RAW / "sram" / "SRAM Straight Line Distance Data.csv", "CensusTract20")
    dd = load_tracts(RAW / "sram" / "SRAM Driving Distance Data.csv", "CensusTract20")
    drop = ["CensusTract20", "State", "County20", "County24", "county_fips"]
    return gen.merge(sd.drop(columns=drop), on="tract").merge(dd.drop(columns=drop), on="tract")


def load_lram():
    df = load_tracts(RAW / "lram" / "Food Access Research Atlas.csv", "CensusTract")
    return df.rename(columns={"Pop2010": "POP"})


def summarize(df, pop, flags, lapop, lalowi, label):
    """Tract counts and populations for one map/measure, split rural vs urban."""
    rows = []
    for urban, g in [("all", df), ("rural", df[df["Urban"] == 0]), ("urban", df[df["Urban"] == 1])]:
        rows.append({
            "measure": label,
            "area": urban,
            "tracts": len(g),
            "population": g[pop].sum(),
            "LA_tracts_1_10": int(g[flags["LA"]].sum()),
            "LILA_tracts_1_10": int(g[flags["LILA"]].sum()),
            "LA_pop_1_10": g[lapop].sum(),
            "LA_pop_share_pct": 100 * g[lapop].sum() / g[pop].sum(),
            "LA_lowincome_pop_1_10": g[lalowi].sum(),
        })
    return rows


def main():
    arc = load_arc()
    sram = load_sram().merge(arc, on="county_fips", how="left")
    lram = load_lram().merge(arc, on="county_fips", how="left")
    sram["appalachia"] = sram["subregion"].notna()
    lram["appalachia"] = lram["subregion"].notna()

    print(f"ARC counties: {len(arc)}; matched in SRAM: {sram.loc[sram.appalachia, 'county_fips'].nunique()}, "
          f"in LRAM: {lram.loc[lram.appalachia, 'county_fips'].nunique()}")

    # --- Region-level summary (tract-based counts, 1 mi urban / 10 mi rural) ---
    rows = []
    for region, s, l in [
        ("Appalachia", sram[sram.appalachia], lram[lram.appalachia]),
        ("Rest of US", sram[~sram.appalachia], lram[~lram.appalachia]),
    ]:
        for r in (
            summarize(l, "POP", {"LA": "LA1and10", "LILA": "LILATracts_1And10"},
                      "LAPOP1_10", "LALOWI1_10", "LRAM 2019 supermarkets, straight-line")
            + summarize(s, "POP2020", {"LA": "SD_SRAM_LA1and10", "LILA": "SD_SRAM_LILATracts_1And10"},
                        "SD_SRAM_LAPOP1_10", "SD_SRAM_LALOWI1_10", "SRAM 2025 all SNAP stores, straight-line")
            + summarize(s, "POP2020", {"LA": "DD_SRAM_LA1and10", "LILA": "DD_SRAM_LILATracts_1And10"},
                        "DD_SRAM_LAPOP1_10", "DD_SRAM_LALOWI1_10", "SRAM 2025 all SNAP stores, driving")
        ):
            rows.append({"region": region, **r})
    region = pd.DataFrame(rows)
    region.to_csv(OUT / "region_summary.csv", index=False)
    pd.set_option("display.width", 250, "display.max_columns", 20)
    print("\n=== Region summary (1 mi urban / 10 mi rural) ===")
    print(region.round(1).to_string(index=False))

    # --- Q2 at tract level: straight-line vs driving, Appalachia by subregion ---
    a = sram[sram.appalachia].copy()
    a["flip_to_LA_by_driving"] = (a["SD_SRAM_LA1and10"] == 0) & (a["DD_SRAM_LA1and10"] == 1)
    a["flip_to_LILA_by_driving"] = (a["SD_SRAM_LILATracts_1And10"] == 0) & (a["DD_SRAM_LILATracts_1And10"] == 1)
    a["extra_LA_pop_driving"] = a["DD_SRAM_LAPOP1_10"] - a["SD_SRAM_LAPOP1_10"]
    sub = a.groupby(["subregion", "Urban"]).agg(
        tracts=("tract", "size"),
        pop=("POP2020", "sum"),
        LA_SD=("SD_SRAM_LA1and10", "sum"),
        LA_DD=("DD_SRAM_LA1and10", "sum"),
        LILA_SD=("SD_SRAM_LILATracts_1And10", "sum"),
        LILA_DD=("DD_SRAM_LILATracts_1And10", "sum"),
        LApop_SD=("SD_SRAM_LAPOP1_10", "sum"),
        LApop_DD=("DD_SRAM_LAPOP1_10", "sum"),
        rural10_SD=("SD_SRAM_lapop10", "sum"),
        rural10_DD=("DD_SRAM_lapop10", "sum"),
    ).reset_index()
    sub["LApop_ratio_DD_over_SD"] = sub["LApop_DD"] / sub["LApop_SD"]
    sub["pop10mi_ratio_DD_over_SD"] = sub["rural10_DD"] / sub["rural10_SD"]
    sub.to_csv(OUT / "appalachia_subregion_sd_vs_dd.csv", index=False)
    print("\n=== Appalachia by subregion: straight-line (SD) vs driving (DD), SRAM 2025 ===")
    print(sub.round(2).to_string(index=False))

    # --- Fixed-distance shares in rural tracts (sidesteps the 1-mi urban / 10-mi rural switch) ---
    # Each map's own rural flag is used; LRAM has no driving measure.
    fixed = []
    for name, df, pop, cols in [
        ("LRAM straight-line", lram, "POP", {"1mi": "lapop1", "10mi": "lapop10", "20mi": "lapop20"}),
        ("SRAM straight-line", sram, "POP2020", {"1mi": "SD_SRAM_lapop1", "10mi": "SD_SRAM_lapop10", "20mi": "SD_SRAM_lapop20"}),
        ("SRAM driving", sram, "POP2020", {"1mi": "DD_SRAM_lapop1", "10mi": "DD_SRAM_lapop10", "20mi": "DD_SRAM_lapop20"}),
    ]:
        r = df[df["Urban"] == 0]
        groups = [("Rest of US", r[~r.appalachia])] + [(s, g) for s, g in r[r.appalachia].groupby("subregion")]
        for gname, g in groups:
            fixed.append({"map": name, "group": gname, "rural_pop": g[pop].sum(),
                          **{f"pct_beyond_{k}": 100 * g[v].sum() / g[pop].sum() for k, v in cols.items()}})
    fixed = pd.DataFrame(fixed)
    fixed.to_csv(OUT / "rural_fixed_distance_shares.csv", index=False)
    print("\n=== Rural tracts: % of people beyond fixed distances from nearest store ===")
    print(fixed.round(2).to_string(index=False))

    # --- Q1 at county level: LRAM vs SRAM low-access population share ---
    def county(df, pop, lapop, lapop10, prefix):
        g = df.groupby("county_fips").agg(pop=(pop, "sum"), la=(lapop, "sum"), la10=(lapop10, "sum"))
        g[f"{prefix}_LA_share"] = 100 * g["la"] / g["pop"]
        g[f"{prefix}_beyond10mi_share"] = 100 * g["la10"] / g["pop"]
        return g.add_prefix("").rename(columns={"pop": f"{prefix}_pop", "la": f"{prefix}_LA_pop", "la10": f"{prefix}_beyond10mi_pop"})

    names = sram.groupby("county_fips").agg(state=("State", "first"), county=("County20", "first"),
                                             subregion=("subregion", "first"),
                                             rural_pop_share=("POP2020", lambda s: 0))
    rural = sram.assign(rp=sram["POP2020"] * (sram["Urban"] == 0)).groupby("county_fips")
    names["rural_pop_share"] = 100 * rural["rp"].sum() / rural["POP2020"].sum()
    c = (names
         .join(county(lram, "POP", "LAPOP1_10", "lapop10", "LRAM"))
         .join(county(sram, "POP2020", "SD_SRAM_LAPOP1_10", "SD_SRAM_lapop10", "SRAM_SD"))
         .join(county(sram, "POP2020", "DD_SRAM_LAPOP1_10", "DD_SRAM_lapop10", "SRAM_DD")))
    c = c[c["subregion"].notna()].copy()
    c["store_def_change_pts"] = c["SRAM_SD_LA_share"] - c["LRAM_LA_share"]
    c["driving_change_pts"] = c["SRAM_DD_LA_share"] - c["SRAM_SD_LA_share"]
    c.reset_index().to_csv(OUT / "appalachia_county_comparison.csv", index=False)

    cols = ["state", "county", "subregion", "rural_pop_share", "LRAM_LA_share",
            "SRAM_SD_LA_share", "SRAM_DD_LA_share", "store_def_change_pts", "driving_change_pts"]
    print("\n=== Appalachian counties: biggest drops in low-access share, LRAM -> SRAM (straight-line) ===")
    print(c.sort_values("store_def_change_pts")[cols].head(15).round(1).to_string())
    print("\n=== Biggest increases from straight-line -> driving (SRAM) ===")
    print(c.sort_values("driving_change_pts", ascending=False)[cols].head(15).round(1).to_string())
    print("\n=== Subregion means of county-level changes (pct points) ===")
    print(c.groupby("subregion")[["LRAM_LA_share", "SRAM_SD_LA_share", "SRAM_DD_LA_share",
                                   "store_def_change_pts", "driving_change_pts"]].mean().round(1))
    print("\n=== East TN Appalachian counties ===")
    print(c[c["state"] == "Tennessee"].sort_values("LRAM_LA_share", ascending=False)[cols].round(1).to_string())


if __name__ == "__main__":
    main()
