"""
GeoPulse - Week 2 (pure Python): pings within 500 m of each store.
Run from the main GeoPulse folder: python spark_jobs/spatial_join_python.py
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

R = 6371000.0  # Earth radius in metres


def to_xy(lat, lon, lat0):
    # Local flat projection in metres. Accurate to a few metres over a city.
    x = np.radians(lon) * R * np.cos(np.radians(lat0))
    y = np.radians(lat) * R
    return np.column_stack([x, y])


def main(a):
    pings = pd.read_csv(Path(a.data, "pings.csv"))
    stores = pd.read_csv(Path(a.data, "stores.csv"))
    print("Total pings:", len(pings))

    lat0 = pings["lat"].mean()
    p_xy = to_xy(pings["lat"].values, pings["lon"].values, lat0)
    s_xy = to_xy(stores["lat"].values, stores["lon"].values, lat0)

    tree = cKDTree(p_xy)
    hits = tree.query_ball_point(s_xy, r=a.radius)

    frames = []
    for store_id, sxy, idx in zip(stores["store_id"], s_xy, hits):
        if len(idx) == 0:
            continue
        idx = np.array(idx)
        part = pings.iloc[idx][["device_id", "ping_ts", "lat", "lon"]].copy()
        part.insert(0, "store_id", store_id)
        part["dist_m"] = np.hypot(*(p_xy[idx] - sxy).T).round(1)
        frames.append(part)

    visits = pd.concat(frames, ignore_index=True)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    visits.to_csv(Path(a.out, "store_visits.csv"), index=False)

    print("Store visits found:", len(visits))
    print(visits.groupby("store_id")["device_id"].nunique()
          .sort_values(ascending=False).head(10))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data")
    p.add_argument("--out", default="output")
    p.add_argument("--radius", type=float, default=500)
    main(p.parse_args())