from duckdb import connect
from generate_common import get_inserts, intersect_test_wkt, sql_setup

connection = connect()
connection.execute(sql_setup)

for id, parts in get_inserts().items():
    sql = parts[0]
    parameters = parts[1]
    connection.execute(sql, parameters)

connection.execute(
    "COPY (SELECT * EXCLUDE(feature), ST_AsWKB(feature) as feature FROM features) TO '/output/features-100.parquet' (FORMAT PARQUET)"
)
print(
    "1.0.0 intersect count: {}".format(
        len(
            list(
                connection.execute(
                    "SELECT id FROM '/output/features-100.parquet' WHERE ST_Intersects(ST_GeomFromWKB(feature), ST_GeomFromText('{}'));".format(
                        intersect_test_wkt
                    )
                ).fetchall()
            )
        )
    )
)
