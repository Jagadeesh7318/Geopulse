import argparse
from importlib.resources import path
from pathlib import Path
import pandas as pd
import numpy as np

LAT_MIN, LAT_MAX = 12.85,13.10
LON_MIN, LON_MAX = 77.45, 77.75

def main(a):
    rng = np.random.default_rng(a.seed)
    out = path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res_centers = np.column_stack([rng.uniform(LAT_MIN,LAT_MAX,25),rng.uniform(LON_MIN,LON_MAX,25)])
    work_centers = np.column_stack([rng.uniform(12,90,13,05,12),rng.uniform(77,50,77,70,12)])

    s_idx = rng.integers(0, len(work_centers),a.stores)
    s_pts = work_centers[s_idx] + rng.normal(0,0.006,(a.stores,2))
    stores = pd.DataFrame({
        "store_id": np.arange(1, a.stores+1),
        "store_name":[f"store_{i:03d}" for  i in range(1, a.stores +1)],
        "lat":s_pts[:, 0],
        "lon":s_pts[:,1],
     })
    stores.to_csv(out/"stores.csv",index=False)
    home =res_centers[rng.integers(0, len(res_centers),a.devices)] + rng.normal(0,0.01,(a.devices,2))
    work = work_centers[rng.integers(0, len(work_centers),a.devices)]+rng.normal(0,0.004,(a.devices, 2))
    w=np.full(24,0.5)
    w[7:10]=[4,6,4]
    w[12:14]=3
    w[17:20]=[4,6,4]
    w/=w.sum()

    dev = rng.integers(0,a.devices,a.pings)
    day = rng.integers(0,a.days,a.pings)
    hour = rng.choice(24,size=a.pings,p=w)
    minute = rng.integers(0,60,a.pings)
    second = rng.integers(0, 60,a.pings)
    frac =hour + minute/60

    H,W =home[dev], work[dev]
    pos = H.copy
    morning =(frac >= 7) & (frac < 10)
    midday = (frac >= 10) & (frac < 17)
    evening = (frac >=17) & (frac < 20)
    t_m =((frac -7)/3)[:,None]
    t_e = ((frac - 17)/3)[:,None]
    pos = np.where(morning[:,None],H +t_m *(W-H),pos)
    pos = np.where(midday[:,None],W,pos)
    pos = np.where(evening[:,None],W +t_e  * (H-W),pos)
    pos = pos + rng.normal(0,0.007,pos.shape)#~80 m GPS noise