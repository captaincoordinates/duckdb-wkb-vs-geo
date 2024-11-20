from os import environ, path
from pickle import dump, load
from random import uniform
from typing import Any, Dict, Final, Tuple

from shapely.geometry import Polygon
from shapely.wkt import dumps as wkt_dump

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
        feature GEOMETRY NOT NULL,
        x_min FLOAT NOT NULL,
        y_min FLOAT NOT NULL,
        x_max FLOAT NOT NULL,
        y_max FLOAT NOT NULL,
    );                  
"""
intersect_test_wkt: Final[str] = (
    "POLYGON ((-180 -90, 180 -90, 180 90, -180 90, -180 -90))"
)


def get_inserts() -> Dict[int, Tuple[str, Tuple[Any]]]:
    cache_path = path.join(
        path.dirname(__file__), ".cache", f"inserts_{_feature_count}.pkl"
    )
    if not path.exists(cache_path):
        inserts_dict: Dict[int, Tuple[str, Tuple[Any]]] = {}
        # Could utilise parallelism for better performance, but probably not
        # worth the effort as will likely only run once.
        for i in range(_feature_count):
            if i % _feature_report_interval == 0:
                print(f"generating feature {i + 1} of {_feature_count}")
            x1 = round(uniform(_x_min, _x_max - _minimum_span), 6)
            x2 = round(uniform(x1, min(_x_max, x1 + _maximum_span)), 6)
            y1 = round(uniform(_y_min, _y_max - _minimum_span), 6)
            y2 = round(uniform(y1, min(_y_max, y1 + _maximum_span)), 6)
            feature = Polygon(
                [
                    (x1, y1),
                    (x2, y1),
                    (x2, y2),
                    (x1, y2),
                    (x1, y1),
                ]
            )
            inserts_dict[i] = (
                f"INSERT INTO features (id, feature, x_min, y_min, x_max, y_max) VALUES (?, ST_GeomFromText('{wkt_dump(feature)}'), ?, ?, ?, ?)",
                (i, *feature.bounds),
            )
        with open(cache_path, "wb") as f:
            dump(inserts_dict, f)
            return inserts_dict
    with open(cache_path, "rb") as f:
        return load(f)
