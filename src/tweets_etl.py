from tqdm import tqdm
import pandas as pd
import resources
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None  # default='warn'


def process_tweets(data):

    df_twt = pd.DataFrame()
    ref_type = {"replied_to": "reply", "quoted": "quote", "retweeted": "retweet", "tweet": "tweet"}

    for j in tqdm(data["data"]):
        dt_twt = dict()
        dt_twt["id"] = j["id"]
        dt_twt["user_id"] = j["author_id"]
        try:
            tweet_type = j["referenced_tweets"][0]["type"]
        except KeyError:
            tweet_type = "tweet"
        dt_twt["type"] = ref_type[tweet_type]
        dt_twt["created_at"] = j["created_at"]
        dt_twt["conversation_id"] = j["conversation_id"]
        try:
            dt_twt["replying_to_user_id"] = j["in_reply_to_user_id"]
        except KeyError:
            dt_twt["replying_to_user_id"] = None
        try:
            dt_twt["referenced_tweet_id"] = j["referenced_tweets"][0]["id"]
        except KeyError:
            dt_twt["referenced_tweet_id"] = None
        dt_twt["likes"] = j["public_metrics"]["like_count"]
        dt_twt["quotes"] = j["public_metrics"]["quote_count"]
        dt_twt["replies"] = j["public_metrics"]["reply_count"]
        dt_twt["retweets"] = j["public_metrics"]["retweet_count"]
        dt_twt["text"] = j["text"]

        df_twt_aux = pd.DataFrame(list([dt_twt.values()]), columns=list(dt_twt.keys()))
        df_twt = pd.concat([df_twt, df_twt_aux], ignore_index=True)

    return df_twt


def process_tweet_entities(data):

    df_ent = pd.DataFrame()
    ref_ent = {"hashtags": "tag", "mentions": "username", "urls": "expanded_url", "media": "media_url_https",
               "symbols": "text", "cashtags": "tag"}

    for j in tqdm(data["data"]):
        if "entities" in j.keys():
            for k, v in j["entities"].items():
                if k == "annotations":
                    pass
                else:
                    for item in v:
                        dt_ent = dict()
                        dt_ent["tweet_id"] = j["id"]
                        dt_ent["type"] = k[:-1] if k[-1] == "s" else k
                        dt_ent["content"] = item[ref_ent[k]] if k != "polls" else None
                        df_ent_aux = pd.DataFrame(list([dt_ent.values()]), columns=list(dt_ent.keys()))
                        df_ent = pd.concat([df_ent, df_ent_aux], ignore_index=True)

    return df_ent


def etl_tweets(ti):
    s3_file = ti.xcom_pull(key="latest_tweets_data_file", task_ids="twitter_tweets_ingestion")
    tweets_data = resources.read_s3_file(s3_file)
    df_tweets = process_tweets(tweets_data)
    db_conn = resources.connect_to_database()
    resources.insert_batch(
        conn=db_conn,
        dataframe=df_tweets,
        schema="twitter",
        table="tweets",
        conflict=True,
        conflict_column="id"
    )
    db_conn.close()


def etl_tweet_entities(ti):
    s3_file = ti.xcom_pull(key="latest_tweets_data_file", task_ids="twitter_tweets_ingestion")
    tweets_data = resources.read_s3_file(s3_file)
    df_tweet_entities = process_tweet_entities(tweets_data)
    db_conn = resources.connect_to_database()
    resources.insert_batch(
        conn=db_conn,
        dataframe=df_tweet_entities,
        schema="twitter",
        table="tweet_entities",
        conflict=False
    )
    db_conn.close()
