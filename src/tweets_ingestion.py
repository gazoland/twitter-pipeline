from datetime import datetime
from tqdm import tqdm
import resources


def read_user_ids():
    db_conn = resources.connect_to_database()
    cur = db_conn.cursor()
    cur.execute("SELECT username_id FROM twitter.usernames")
    user_ids = [u[0] for u in cur.fetchall()]

    db_conn.close()
    return user_ids


def get_last_tweets(user_list):
    conn = resources.connect_to_database()
    cur = conn.cursor()
    qry = """
            SELECT t.user_id, MAX(t.id) last_tweet 
            FROM twitter.tweets t
            GROUP BY t.user_id
            ORDER BY t.user_id DESC;
        """
    cur.execute(qry)
    db_users_tweets = {x[0]: x[1] for x in cur.fetchall()}
    users_last_tweets = {user_id: db_users_tweets[user_id] if user_id in db_users_tweets.keys() else None
                         for user_id in user_list}
    cur.close()
    conn.close()
    return users_last_tweets


def user_timelines_url(user_id, last_tweet_id, pag_token):
    tweet_fields = ["created_at", "entities", "in_reply_to_user_id", "public_metrics", "referenced_tweets", "author_id",
                    "conversation_id"]
    t_fields = f"tweet.fields={','.join(tweet_fields)}"

    since = f"&since_id={last_tweet_id}" if last_tweet_id is not None else ""

    if not pag_token:
        url = "https://api.twitter.com/2/users/{}/tweets?{}&{}&start_time=2022-01-01T00:00:00Z&" \
              "max_results=100".format(user_id, t_fields, since)
    else:
        url = "https://api.twitter.com/2/users/{}/tweets?{}&{}&start_time=2022-01-01T00:00:00Z&" \
              "max_results=100&pagination_token={}".format(user_id, t_fields, since, pag_token)
    return url


def ingest_tweets(ti):
    ids = read_user_ids()
    user_tweet = get_last_tweets(ids)
    tweets_data = {"data": []}
    for u_id, t_id in tqdm(user_tweet.items(), total=len(user_tweet.keys())):
        next_token = False
        while next_token is not None:
            url_timeline = user_timelines_url(u_id, t_id, next_token)
            resp = resources.connect_to_endpoint(url_timeline)
            try:
                tweets_data["data"].extend(resp["data"])
            except KeyError:
                print(f"No new tweets from user_id: {u_id}")
                pass
            try:
                next_token = resp["meta"]["next_token"]
            except KeyError:
                next_token = None

    tweets_filename = f"tweets_{datetime.strftime(datetime.today(), '%Y%m%d')}.txt"
    path = "data/tweets/"
    resources.write_json_file(tweets_data, tweets_filename)
    resources.upload_to_s3(tweets_filename, path=path)
    resources.delete_file(tweets_filename)
    ti.xcom_push(key="latest_tweets_data_file", value=path + tweets_filename)
