from tqdm import tqdm
import pandas as pd
import resources
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None  # default='warn'


def process_users(data):
    df = pd.DataFrame()
    for j in tqdm(data["data"]):
        dt = dict()
        dt["id"] = j["id"]
        dt["username"] = j["username"]
        dt["name"] = j["name"]
        dt["verified"] = j["verified"]
        dt["created_at"] = j["created_at"]
        desc = j["description"]
        if "https://" in desc:
            links_dict = {y["url"]: y["display_url"] for y in j["entities"]["description"]["urls"]}
            for k, v in links_dict.items():
                desc = desc.replace(k, v)
        dt["description"] = desc
        df_unit = pd.DataFrame([list(dt.values())], columns=list(dt.keys()))
        # df = df.append(dt, ignore_index=True)
        df = pd.concat([df, df_unit], ignore_index=True)
    return df


def process_users_metrics(data):
    df = pd.DataFrame()
    for j in tqdm(data["data"]):
        dt = dict()
        dt["user_id"] = j["id"]
        dt["followers"] = j["public_metrics"]["followers_count"]
        dt["following"] = j["public_metrics"]["following_count"]
        dt["tweets"] = j["public_metrics"]["tweet_count"]
        dt["listed"] = j["public_metrics"]["listed_count"]
        dt["created_at"] = data["created_at"]

        df_unit = pd.DataFrame([list(dt.values())], columns=list(dt.keys()))
        # df = df.append(dt, ignore_index=True)
        df = pd.concat([df, df_unit], ignore_index=True)
    return df


def etl_users(ti):
    s3_file = ti.xcom_pull(key="latest_user_data_file", task_ids="twitter_users_ingestion")
    user_data = resources.read_s3_file(s3_file)
    df_user = process_users(user_data)
    db_conn = resources.connect_to_database()
    resources.upsert_batch(
        conn=db_conn,
        dataframe=df_user,
        schema="twitter",
        table="users",
        conflict=True,
        conflict_column="id"
    )
    db_conn.close()


def etl_user_metrics(ti):
    s3_file = ti.xcom_pull(key="latest_user_data_file", task_ids="twitter_users_ingestion")
    user_data = resources.read_s3_file(s3_file)
    df_user_metrics = process_users_metrics(user_data)
    db_conn = resources.connect_to_database()
    resources.insert_batch(
        conn=db_conn,
        dataframe=df_user_metrics,
        schema="twitter",
        table="user_metrics",
        conflict=False
    )
    db_conn.close()
