from duckdb import connect
from typing import Dict
from shapely.geometry import Polygon
from shapely.wkt import dumps as wkt_dump
from time import time
from json import dumps

timing_precision = 3
parquet_100_path = "/parquet/features-100.parquet"
parquet_113_path = "/parquet/features-113.parquet"

connection = connect()
connection.execute("""
    INSTALL spatial;
    LOAD spatial;
""")
# attempt to avoid any benchmarking disadvantages from .parquet access ordering
connection.execute(f"SELECT COUNT(*) FROM '{parquet_100_path}'")
connection.execute(f"SELECT COUNT(*) FROM '{parquet_113_path}'")

shapes = {
    "Smithers": Polygon([(-127.3686, 54.6826), (-126.9697, 54.6826), (-126.9697, 54.8414), (-127.3686, 54.8414), (-127.3686, 54.6826)]),
    "Wyoming": Polygon([(-110.610, 41.698), (-104.227, 41.698), (-104.227, 44.903), (-110.610, 44.903), (-110.610, 41.698)]),
    "Madrid": Polygon([(-3.80522, 40.35936), (-3.60575, 40.35936), (-3.60575, 40.46419), (-3.80522, 40.46419), (-3.80522, 40.35936)]),
    "Kadoma": Polygon([(29.84891, -18.37351), (29.94864, -18.37351), (29.94864, -18.30817), (29.84891, -18.30817), (29.84891, -18.37351)]),
    "Air Molek": Polygon([(102.24332, -0.40177), (102.34305, -0.40177), (102.34305, -0.33294), (102.24332, -0.33294), (102.24332, -0.40177)]),
}

times: Dict[str, Dict[str, float]] = {
    "100": {},
    "113": {},
}
for name, shape in shapes.items():
    wkt = wkt_dump(shape)

    start_100 = time()
    connection.execute(f"""
        SELECT id
          FROM '{parquet_100_path}'
         WHERE ST_Intersects(ST_GeomFromWKB(feature), ST_GeomFromText('{wkt}'))               
    """)
    times["100"][name] = round(time() - start_100, timing_precision)
    
    start_113 = time()
    connection.execute(f"""
        SELECT id
          FROM '{parquet_113_path}'
         WHERE ST_Intersects(feature, ST_GeomFromText('{wkt}'))     
    """)
    times["113"][name] = round(time() - start_113, timing_precision)

print(dumps(times, indent=2))
