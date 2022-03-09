import psycopg2.extras
import time
from tqdm import tqdm
import os
import pandas as pd
import numpy as np


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


def upsert(conn, df, table, conflict_column):
    con = psycopg2.connect(
        host='',
        user='',
        password='',
        dbname='',
        port=0
    )

    cur = con.cursor()
    cols = ','.join(list(df))
    vals = ','.join(['%s'] * len(list(df)))
    updates = ','.join([x + '=%s' for x in list(df)[1:]])
    rows = [list(x) for x in df.to_numpy()]
    qry = f"insert into {table} ({cols}) values ({vals}) on conflict ({conflict_column}) do update set {updates}"
    time.sleep(0.2)
    for i in tqdm(rows):
        i.extend(i[1:])
        j = [None if pd.isna(x) else x for x in i]
        k = [int(y) if type(y) == np.int64 else y for y in j]
        try:
            cur.execute(qry, tuple(k))
        except psycopg2.ProgrammingError as pgerr:
            print(updates)
            for x in k:
                print(x, type(x), pgerr)
                con.close()
                input('dsg')
        con.commit()
    con.close()
    print('Done.')


def insert_batch(conn, dataframe, schema, table, conflict: bool, conflict_column=None):

    tuples = [tuple(x) for x in dataframe.to_numpy()]
    cols = ','.join(list(dataframe.columns))
    aux = '(' + '%s,' * (len(tuples[0]) - 1) + '%s)'
    if conflict:
        query = f"INSERT INTO {schema}.{table} ({cols}) VALUES {aux} ON CONFLICT ({conflict_column}) DO NOTHING"
    else:
        query = f"INSERT INTO {schema}.{table} ({cols}) VALUES {aux}"

    cursor = conn.cursor()
    psycopg2.extras.execute_batch(cursor, query, tuples)
    conn.commit()
    cursor.close()
    # conn.close()
    print('Done')
