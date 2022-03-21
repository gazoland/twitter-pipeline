import pandas as pd
import resources


def process_tweet_metrics(data):
    t_metrics = [
        {
            "id": t["id"],
            "likes": t["public_metrics"]["like_count"],
            "quotes": t["public_metrics"]["quote_count"],
            "replies": t["public_metrics"]["reply_count"],
            "retweets": t["public_metrics"]["retweet_count"]} for t in data["data"]]

    df = pd.DataFrame(t_metrics)

    return df


def etl_tweet_metrics(ti):
    s3_file = ti.xcom_pull(key="latest_tweet_metrics_data_file", task_ids="twitter_tweet_metrics_ingestion")
    tweet_metrics_data = resources.read_s3_file(s3_file)
    df_tweet_metrics = process_tweet_metrics(tweet_metrics_data)
    db_conn = resources.connect_to_database()
    resources.update_batch(
        conn=db_conn,
        dataframe=df_tweet_metrics,
        schema="twitter",
        table="tweets",
        include_columns=list(df_tweet_metrics),
        where_columns=["id", ]
    )
    db_conn.close()
