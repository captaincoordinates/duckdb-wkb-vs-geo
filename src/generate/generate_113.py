from duckdb import connect
from generate_common import get_inserts, intersect_test_wkt, sql_setup

connection = connect()
connection.execute(sql_setup)

for id, sql in get_inserts().items():
    connection.execute(sql, [id])

connection.execute(
    "COPY (SELECT * FROM features) TO '/output/features-113.parquet' (FORMAT PARQUET)"
)
print(
    "1.1.3 intersect count: {}".format(
        len(
            list(
                connection.execute(
                    "SELECT id FROM '/output/features-113.parquet' WHERE ST_Intersects(feature, ST_GeomFromText('{}'));".format(
                        intersect_test_wkt
                    )
                ).fetchall()
            )
        )
    )
)
