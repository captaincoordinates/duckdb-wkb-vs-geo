from typing import Final
from random import uniform
from shapely.geometry import Polygon
from shapely.wkt import dumps
from duckdb import connect, DuckDBPyConnection

x_min: Final[float] = -180
y_min: Final[float] = -90
x_max: Final[float] = 180
y_max: Final[float] = 90

minimum_span: Final[float] = 0.1
maximum_span: Final[float] = 10

feature_count: Final[int] = 1000
feature_report_interval: Final[int] = max(round(feature_count / 100), 1)

connection: Final[DuckDBPyConnection] = connect()
connection.execute("""
    INSTALL SPATIAL;
    LOAD SPATIAL;
    CREATE TABLE features(
        id INT PRIMARY KEY,
        feature GEOMETRY NOT NULL   
    );                  
""")

for i in range(feature_count):
    if i % feature_report_interval == 0:
        print(f"processing feature {i}")
    x1 = round(uniform(x_min, x_max - minimum_span), 6)
    x2 = round(uniform(x1, min(x_max, x1 + maximum_span)), 6)
    y1 = round(uniform(y_min, y_max - minimum_span), 6)
    y2 = round(uniform(y1, min(y_max, y1 + maximum_span)), 6)
    feature = Polygon([
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (x1, y2),
        (x1, y1),
    ])
    connection.execute(f"INSERT INTO features (id, feature) VALUES (?, ST_GeomFromText('{dumps(feature)}'))", [i])

connection.execute("COPY (SELECT * FROM features) TO '/output/features-geometry.parquet' (FORMAT PARQUET)")
connection.execute("COPY (SELECT id, ST_AsWKB(feature) as feature FROM features) TO '/output/features-wkb.parquet' (FORMAT PARQUET)")
