from datetime import datetime, timezone
import resources
import pandas as pd
from tqdm import tqdm


def users_url():
    conn = resources.connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT username FROM twitter.usernames")
    users = ",".join([u[0] for u in cur.fetchall()])

    cur.execute("SELECT username FROM twitter.usernames WHERE username_id IS NULL")
    no_id_users = [u[0] for u in cur.fetchall()]

    conn.close()

    user_fields = ["description", "created_at", "public_metrics", "verified", "entities"]

    u_fields = f"user.fields={','.join(user_fields)}"
    usernames = f"usernames={users}"
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, u_fields)

    return url, no_id_users


def insert_missing_ids(datafile, no_id_users):
    df = pd.DataFrame(columns=["username", "username_id"])

    for user in tqdm(datafile["data"]):
        if user["username"].lower() in no_id_users:
            # df = df.append({user["username"]: user["id"]}, ignore_index=True)
            df_unit = pd.DataFrame([[user["username"].lower(), user["id"]]], columns=["username", "username_id"])
            df = pd.concat([df, df_unit], ignore_index=True)

    if df.size > 0:
        print(f"{df.size} users without username_id. Inserting them now.")
        db_conn = resources.connect_to_database()
        resources.update_batch(
            conn=db_conn,
            dataframe=df,
            schema="twitter",
            table="usernames",
            include_columns=["username", "username_id"],
            where_columns="username")
        db_conn.close()
        print("Done")


def user_file_creation(datafile):
    user_data_filename = f"users_{datetime.strftime(datetime.today(), '%Y%m%d')}.txt"
    resources.write_json_file(datafile, user_data_filename)

    user_ids = dict()
    for user in datafile["data"]:
        user_ids[user["username"]] = user["id"]
    resources.write_json_file(user_ids, "user_ids.txt")

    return user_data_filename


def ingest_users(ti):
    url, users_without_id = users_url()
    user_data = resources.connect_to_endpoint(url)
    if len(users_without_id) > 0:
        insert_missing_ids(user_data, users_without_id)
    user_data["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    user_data_filename = user_file_creation(user_data)
    path = "data/users/"
    resources.upload_to_s3(user_data_filename, path=path)
    resources.delete_file(user_data_filename)
    ti.xcom_push(key="latest_user_data_file", value=path + user_data_filename)
