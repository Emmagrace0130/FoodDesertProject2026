"""Download 2020 Census block internal points + population for every ARC county.

Uses the TIGERweb REST service (no geometry), one cached CSV per county in
data/raw/blocks/. Safe to re-run; finished counties are skipped.

Run from the project root:  .venv/bin/python analysis/02_fetch_blocks.py
"""
import csv
import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

import certifi
import pandas as pd

SSL_CTX = ssl.create_default_context(cafile=certifi.where())
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "blocks"
OUT.mkdir(parents=True, exist_ok=True)
URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2020/MapServer/10/query"
PAGE = 50000


def fetch_county(fips):
    rows, offset = [], 0
    while True:
        params = urllib.parse.urlencode({
            "where": f"STATE='{fips[:2]}' AND COUNTY='{fips[2:]}' AND POP100>0",
            "outFields": "GEOID,POP100,UR,INTPTLAT,INTPTLON",
            "returnGeometry": "false", "f": "json",
            "resultOffset": offset, "resultRecordCount": PAGE, "orderByFields": "GEOID",
        })
        with urllib.request.urlopen(f"{URL}?{params}", timeout=120, context=SSL_CTX) as r:
            data = json.load(r)
        if "error" in data:
            raise RuntimeError(f"{fips}: {data['error']}")
        rows += [f["attributes"] for f in data["features"]]
        if not data.get("exceededTransferLimit"):
            return rows
        offset += PAGE


def main():
    arc = pd.read_excel(ROOT / "data" / "raw" / "arc" / "subregions2021.xlsx", header=4, dtype=str)
    counties = arc["FIPS"].dropna().str.zfill(5).tolist()
    for i, fips in enumerate(counties, 1):
        path = OUT / f"{fips}.csv"
        if path.exists():
            continue
        for attempt in range(3):
            try:
                rows = fetch_county(fips)
                break
            except Exception as e:  # network hiccups: back off and retry
                print(f"  retry {fips} ({e})")
                time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f"failed on {fips}")
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["GEOID", "POP100", "UR", "INTPTLAT", "INTPTLON"])
            w.writeheader()
            w.writerows(rows)
        tmp.rename(path)
        print(f"[{i}/{len(counties)}] {fips}: {len(rows)} populated blocks")
        time.sleep(0.3)


if __name__ == "__main__":
    main()
