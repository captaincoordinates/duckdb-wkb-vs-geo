from json import dumps
from os import environ, path
from re import sub
from time import time
from typing import Dict

from duckdb import connect
from shapely.geometry import Polygon
from shapely.wkt import dumps as wkt_dump

connection = connect()
connection.execute("""
    INSTALL spatial;
    LOAD spatial;
""")

parquet_100_file = "features-100.parquet"
parquet_113_file = "features-113.parquet"
path_type = None
file_path_prefix = environ.get("DDB_BENCH_PATH_PREFIX", "/parquet")
if file_path_prefix.startswith("s3://"):
    path_type = "S3"
    file_path_prefix = sub(r"/$", "", file_path_prefix)
    parquet_100_path = "{}/{}".format(file_path_prefix, parquet_100_file)
    parquet_113_path = "{}/{}".format(file_path_prefix, parquet_113_file)
    connection.execute("""
        INSTALL httpfs;
        LOAD httpfs;
    """)
    connection.execute("CREATE SECRET (TYPE S3, PROVIDER CREDENTIAL_CHAIN)")
elif file_path_prefix.startswith(path.sep):
    path_type = "Local File"
    parquet_100_path = path.join(file_path_prefix, parquet_100_file)
    parquet_113_path = path.join(file_path_prefix, parquet_113_file)
else:
    raise Exception("Path prefix not recognised")

timing_precision = 3

# attempt to avoid any benchmarking disadvantages from .parquet access ordering
connection.execute(f"SELECT COUNT(*) FROM '{parquet_100_path}'")
connection.execute(f"SELECT COUNT(*) FROM '{parquet_113_path}'")

shapes = {
    "Smithers": Polygon(
        [
            (-127.3686, 54.6826),
            (-126.9697, 54.6826),
            (-126.9697, 54.8414),
            (-127.3686, 54.8414),
            (-127.3686, 54.6826),
        ]
    ),
    "Wyoming": Polygon(
        [
            (-110.610, 41.698),
            (-104.227, 41.698),
            (-104.227, 44.903),
            (-110.610, 44.903),
            (-110.610, 41.698),
        ]
    ),
    "Madrid": Polygon(
        [
            (-3.80522, 40.35936),
            (-3.60575, 40.35936),
            (-3.60575, 40.46419),
            (-3.80522, 40.46419),
            (-3.80522, 40.35936),
        ]
    ),
    "Kadoma": Polygon(
        [
            (29.84891, -18.37351),
            (29.94864, -18.37351),
            (29.94864, -18.30817),
            (29.84891, -18.30817),
            (29.84891, -18.37351),
        ]
    ),
    "Air Molek": Polygon(
        [
            (102.24332, -0.40177),
            (102.34305, -0.40177),
            (102.34305, -0.33294),
            (102.24332, -0.33294),
            (102.24332, -0.40177),
        ]
    ),
}

name_100_bbox = f"100-bbox ({path_type})"
name_113_geo = f"113-geo ({path_type})"
name_113_bbox = f"113-bbox ({path_type})"
times: Dict[str, Dict[str, float]] = {
    name_100_bbox: {},
    name_113_geo: {},
    name_113_bbox: {},
}
for name, shape in shapes.items():
    wkt = wkt_dump(shape)

    start_100 = time()
    count_100 = connection.execute(
        f"""
        SELECT COUNT(*)
          FROM '{parquet_100_path}'
         WHERE 
           NOT (
                   x_max < ?
                OR y_max < ?
                OR x_min > ?
                OR y_min > ?
              )
           AND ST_Intersects(ST_GeomFromWKB(feature), ST_GeomFromText('{wkt}'))               
        """,
        shape.bounds,
    ).fetchall()[0][0]
    times[name_100_bbox][name] = round(time() - start_100, timing_precision)

    start_113_geo = time()
    count_113_geo = connection.execute(f"""
        SELECT COUNT(*)
          FROM '{parquet_113_path}'
         WHERE ST_Intersects(feature, ST_GeomFromText('{wkt}'))     
    """).fetchall()[0][0]
    times[name_113_geo][name] = round(time() - start_113_geo, timing_precision)

    start_113_bbox = time()
    count_113_bbox = connection.execute(
        f"""
        SELECT COUNT(*)
          FROM '{parquet_113_path}'
         WHERE 
           NOT (
                   x_max < ?
                OR y_max < ?
                OR x_min > ?
                OR y_min > ?
               )
           AND ST_Intersects(feature, ST_GeomFromText('{wkt}'))     
        """,
        shape.bounds,
    ).fetchall()[0][0]
    times[name_113_bbox][name] = round(time() - start_113_bbox, timing_precision)

    assert (
        count_100 == count_113_geo == count_113_bbox
    ), f"result count discrepancy in {name}. 100: {count_100}, 113-geo: {count_113_geo}, 113-bbox: {count_113_bbox}"

print(dumps(times, indent=2))
