from generate_common import sql_setup, get_inserts, intersect_test_wkt
from duckdb import connect

connection = connect()
connection.execute(sql_setup)

for id, sql in get_inserts().items():
    connection.execute(sql, [id])

connection.execute("COPY (SELECT id, ST_AsWKB(feature) as feature FROM features) TO '/output/features-100.parquet' (FORMAT PARQUET)")
print("1.0.0 intersect count: {}".format(
    len(list(connection.execute("SELECT id FROM '/output/features-100.parquet' WHERE ST_Intersects(ST_GeomFromWKB(feature), ST_GeomFromText('{}'));".format(
        intersect_test_wkt
    )).fetchall())))
)
