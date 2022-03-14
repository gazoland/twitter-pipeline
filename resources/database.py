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


def upsert_batch(conn, dataframe, schema, table, conflict: bool, conflict_column=None):

    cols = ','.join(list(dataframe.columns))
    rows = [list(x) for x in dataframe.to_numpy()]
    vals = '%s,' * (len(rows[0]) - 1) + '%s'
    for i in rows:
        i.extend(i[1:])
    tuples = [tuple(y) for y in rows]
    updates = ','.join([x + '=%s' for x in list(dataframe)[1:]])

    if conflict:
        query = f"INSERT INTO {schema}.{table} ({cols}) VALUES ({vals})" \
                f" ON CONFLICT ({conflict_column}) DO UPDATE SET {updates}"
    else:
        query = f"INSERT INTO {schema}.{table} ({cols}) VALUES ({vals})"

    cursor = conn.cursor()
    psycopg2.extras.execute_batch(cursor, query, tuples)
    conn.commit()
    cursor.close()
    # conn.close()
    print('Done')


def insert_batch(conn, dataframe, schema, table, conflict: bool, conflict_column=None):

    cols = ','.join(list(dataframe.columns))
    tuples = [tuple(x) for x in dataframe.to_numpy()]
    vals = '%s,' * (len(tuples[0]) - 1) + '%s'

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


def update_batch(conn, dataframe, schema, table, include_columns, where_columns):

    df = dataframe[include_columns]

    tuples = [tuple(x) for x in df.to_numpy()]
    vals = '%s,' * (len(tuples[0]) - 1) + '%s'
    update_string = ",".join([f"{c}=${list(df).index(c)}" for c in list(df) if c not in where_columns])
    where_string = " AND ".join([f"{c}=${list(df).index(c)}" for c in list(df) if c in where_columns])

    qry_prepare = f"""
        PREPARE stm_update AS
            UPDATE {schema}.{table} SET {update_string} WHERE {where_string};"""
    qry_execute = f"EXECUTE stm_update ({vals});"
    qry_deallocate = "DEALLOCATE stm_update;"

    cursor = conn.cursor()
    cursor.execute(qry_prepare)
    psycopg2.extras.execute_batch(cursor, qry_execute, tuples, page_size=100)
    cursor.execute(qry_deallocate)
    conn.commit()
    cursor.close()
    # conn.close()
    print('Done')
