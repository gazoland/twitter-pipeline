import psycopg2.extras

import psycopg2.extras
import os

DB_HOST = os.environ.get("PG_DB_HOST")
DB_USER = os.environ.get("PG_DB_USER")
DB_PWD = os.environ.get("PG_DB_PWD")
DB_NAME = os.environ.get("PG_DB_NAME")


def connect_to_database():
    conn_object = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PWD,
        dbname=DB_NAME,
        port=5432
    )
    return conn_object


def insert_batch(conn, multicolumn: bool, data, schema, table, conflict: bool, conflict_column=None,
                 single_column=None):

    if multicolumn:
        cols = ','.join(list(data.columns))
        tuples = [tuple(x) for x in data.to_numpy()]
        vals = '%s,' * (len(tuples[0]) - 1) + '%s'
    else:
        cols = single_column
        vals = "%s"
        tuples = [(u, ) for u in list(data)]
        print(tuples)

    if conflict:
        query = f"INSERT INTO {schema}.{table} ({cols}) VALUES ({vals}) ON CONFLICT ({conflict_column}) DO NOTHING"
    else:
        query = f"INSERT INTO {schema}.{table} ({cols}) VALUES ({vals})"

    cursor = conn.cursor()
    psycopg2.extras.execute_batch(cursor, query, tuples)
    conn.commit()
    cursor.close()
    # conn.close()
    print('Done')


