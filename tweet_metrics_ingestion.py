import resources
from pprint import pprint
from tqdm import tqdm
from datetime import datetime


def get_tweets_to_update(interval_size, interval_unit):
    """
    :param interval_size: int
    :param interval_unit: str -> enum(day,)
    :return: list
    """
    conn = resources.connect_to_database()
    cur = conn.cursor()
    qry = """
                SELECT t.id tweet_id 
                FROM twitter.tweets t
                WHERE t.created_at > CURRENT_DATE - INTERVAL '{}' {}
                ORDER BY t.created_at ASC
            """.format(interval_size, interval_unit)
    cur.execute(qry)
    tweets_list = [t[0] for t in cur.fetchall()]
    cur.close()
    conn.close()
    return tweets_list


def tweets_url(ids_string):
    tweet_fields = ["public_metrics"]
    t_fields = f"tweet.fields={','.join(tweet_fields)}"
    url = "https://api.twitter.com/2/tweets/?ids={}&{}".format(ids_string, t_fields)
    return url


def ingest_tweet_metrics():
    ids = get_tweets_to_update(8, 'day')
    id_sets = [ids[i: i + 100] for i in range(0, len(ids), 100)]
    tweet_metrics_data = {"data": []}
    for id_set in tqdm(id_sets):
        id_string = ",".join(id_set)
        url = tweets_url(id_string)
        resp = resources.connect_to_endpoint(url)
        tweet_metrics_data["data"].extend(resp["data"])

    tweets_metrics_filename = f"t_metrics_{datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')}.txt"
    resources.write_json_file(tweet_metrics_data, tweets_metrics_filename)
    resources.upload_to_s3(tweets_metrics_filename, path="data/tweet-metrics/")
    resources.delete_file(tweets_metrics_filename)


if __name__ == "__main__":
    ingest_tweet_metrics()
