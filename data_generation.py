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
    