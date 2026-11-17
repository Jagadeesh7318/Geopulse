"""
GeoPulse - Week 1: mock anonymized GPS pings + store locations (Bengaluru-style bounds).
Commuters move home -> work (7-10am), stay near work (10am-5pm), work -> home (5-8pm).
Usage: python data_generation.py --devices 20000 --pings 2000000 --days 7
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

LAT_MIN, LAT_MAX = 12.85, 13.10
LON_MIN, LON_MAX = 77.45, 77.75


def main(a):
    rng = np.random.default_rng(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    # City structure: residential and business clusters
    res_centers = np.column_stack([rng.uniform(LAT_MIN, LAT_MAX, 25), rng.uniform(LON_MIN, LON_MAX, 25)])
    work_centers = np.column_stack([rng.uniform(12.90, 13.05, 12), rng.uniform(77.50, 77.70, 12)])

    # Stores sit in business areas
    s_idx = rng.integers(0, len(work_centers), a.stores)
    s_pts = work_centers[s_idx] + rng.normal(0, 0.006, (a.stores, 2))
    stores = pd.DataFrame({
        "store_id": np.arange(1, a.stores + 1),
        "store_name": [f"Store_{i:03d}" for i in range(1, a.stores + 1)],
        "lat": s_pts[:, 0],
        "lon": s_pts[:, 1],
    })
    stores.to_csv(out / "stores.csv", index=False)

    # Each device has a home and a workplace
    home = res_centers[rng.integers(0, len(res_centers), a.devices)] + rng.normal(0, 0.01, (a.devices, 2))
    work = work_centers[rng.integers(0, len(work_centers), a.devices)] + rng.normal(0, 0.004, (a.devices, 2))

    # Time-of-day weights: morning, lunch and evening peaks
    w = np.full(24, 0.5)
    w[7:10] = [4, 6, 4]
    w[12:14] = 3
    w[17:20] = [4, 6, 4]
    w /= w.sum()

    dev = rng.integers(0, a.devices, a.pings)
    day = rng.integers(0, a.days, a.pings)
    hour = rng.choice(24, size=a.pings, p=w)
    minute = rng.integers(0, 60, a.pings)
    second = rng.integers(0, 60, a.pings)
    frac = hour + minute / 60

    H, W = home[dev], work[dev]
    pos = H.copy()
    morning = (frac >= 7) & (frac < 10)
    midday = (frac >= 10) & (frac < 17)
    evening = (frac >= 17) & (frac < 20)
    t_m = ((frac - 7) / 3)[:, None]
    t_e = ((frac - 17) / 3)[:, None]
    pos = np.where(morning[:, None], H + t_m * (W - H), pos)
    pos = np.where(midday[:, None], W, pos)
    pos = np.where(evening[:, None], W + t_e * (H - W), pos)
    pos = pos + rng.normal(0, 0.0007, pos.shape)  # ~80 m GPS noise

    base = pd.Timestamp(a.start)
    secs = day * 86400 + hour * 3600 + minute * 60 + second
    pings = pd.DataFrame({
        "device_id": np.char.add("D", np.char.zfill(dev.astype(str), 6)),
        "lat": pos[:, 0].round(6),
        "lon": pos[:, 1].round(6),
        "ping_ts": base + pd.to_timedelta(secs, unit="s"),
    })
    pings.to_csv(out / "pings.csv", index=False)
    print(f"Wrote {len(pings):,} pings and {len(stores)} stores to {out}/")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--devices", type=int, default=20000)
    p.add_argument("--pings", type=int, default=2_000_000)
    p.add_argument("--stores", type=int, default=100)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--start", default="2026-11-01")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="data")
    main(p.parse_args())