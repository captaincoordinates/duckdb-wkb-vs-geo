from typing import Dict, Final, List
from random import uniform
from shapely.geometry import Polygon
from shapely.wkt import dumps as wkt_dump
from os import path, environ
from json import dump, load

_x_min: Final[float] = -180
_y_min: Final[float] = -90
_x_max: Final[float] = 180
_y_max: Final[float] = 90

_minimum_span: Final[float] = 0.1
_maximum_span: Final[float] = 10

_feature_count: Final[int] = int(environ["DDB_BENCH_FEAT_COUNT"])
_feature_report_interval: Final[int] = max(round(_feature_count / 100), 1)

sql_setup: Final[str] = """
    INSTALL spatial;
    LOAD spatial;
    CREATE TABLE features(
        id INT PRIMARY KEY,
        feature GEOMETRY NOT NULL   
    );                  
"""
intersect_test_wkt: Final[str] = "POLYGON ((-180 -90, 180 -90, 180 90, -180 90, -180 -90))"

def get_inserts() -> Dict[int, str]:
    cache_path = path.join(path.dirname(__file__), ".cache", f"inserts_{_feature_count}.json")
    if not path.exists(cache_path):
        inserts_dict: Dict[int, str] = {}
        for i in range(_feature_count):
            if i % _feature_report_interval == 0:
                print(f"generating feature {i + 1} of {_feature_count}")
            x1 = round(uniform(_x_min, _x_max - _minimum_span), 6)
            x2 = round(uniform(x1, min(_x_max, x1 + _maximum_span)), 6)
            y1 = round(uniform(_y_min, _y_max - _minimum_span), 6)
            y2 = round(uniform(y1, min(_y_max, y1 + _maximum_span)), 6)
            feature = Polygon([
                (x1, y1),
                (x2, y1),
                (x2, y2),
                (x1, y2),
                (x1, y1),
            ])
            inserts_dict[i] = f"INSERT INTO features (id, feature) VALUES (?, ST_GeomFromText('{wkt_dump(feature)}'))"
        with open(cache_path, "w") as f:
            dump(inserts_dict, f)
    with open(cache_path, "r") as f:
        return load(f)
