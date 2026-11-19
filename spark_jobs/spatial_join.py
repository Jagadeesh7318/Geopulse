"""
GeoPulse - Week 2: Sedona spatial join.
Finds every ping within 500 m of a store.
Run from the main GeoPulse folder: python spark_jobs/spatial_join.py
"""
import argparse
import os
import sys
from pathlib import Path
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"


# Make Spark use the Python from your .venv
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from sedona.spark import SedonaContext


def main(a):
    spark = (
        SparkSession.builder.appName("GeoPulseSpatialJoin")
        .config(
            "spark.jars.packages",
            "org.apache.sedona:sedona-spark-shaded-3.5_2.12:1.6.1,"
            "org.datasyslab:geotools-wrapper:1.6.1-28.2",
        )
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )
    sedona = SedonaContext.create(spark)

    pings_path = Path(a.data, "pings.csv").resolve().as_posix()
    stores_path = Path(a.data, "stores.csv").resolve().as_posix()

    pings = sedona.read.option("header", True).option("inferSchema", True).csv(pings_path)
    stores = sedona.read.option("header", True).option("inferSchema", True).csv(stores_path)
    pings.createOrReplaceTempView("pings")
    stores.createOrReplaceTempView("stores")

    # ST_DistanceSphere returns metres. Stores are tiny, so they are broadcast.
    visits = sedona.sql(f"""
        SELECT /*+ BROADCAST(s) */
               s.store_id,
               p.device_id,
               p.ping_ts,
               p.lat,
               p.lon,
               ST_DistanceSphere(
                   ST_Point(CAST(p.lon AS DOUBLE), CAST(p.lat AS DOUBLE)),
                   ST_Point(CAST(s.lon AS DOUBLE), CAST(s.lat AS DOUBLE))
               ) AS dist_m
        FROM pings p, stores s
        WHERE ST_DistanceSphere(
                  ST_Point(CAST(p.lon AS DOUBLE), CAST(p.lat AS DOUBLE)),
                  ST_Point(CAST(s.lon AS DOUBLE), CAST(s.lat AS DOUBLE))
              ) <= {a.radius}
    """)

    print("Total pings:", pings.count())
    out = visits.toPandas()  # avoids the Windows Hadoop (winutils) write problem
    Path(a.out).mkdir(parents=True, exist_ok=True)
    out.to_csv(Path(a.out, "store_visits.csv"), index=False)
    print("Store visits found:", len(out))
    print(out.groupby("store_id")["device_id"].nunique().sort_values(ascending=False).head(10))
    spark.stop()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data")
    p.add_argument("--out", default="output")
    p.add_argument("--radius", type=float, default=500)
    main(p.parse_args())