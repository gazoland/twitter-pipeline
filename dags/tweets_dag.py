import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Adding project directories for airflow
add_dir = [os.path.abspath(os.path.join(__file__, "../..")), os.path.abspath(os.path.join(__file__, "../../src")),
           os.path.abspath(os.path.join(__file__, "../../src/resources"))]
[sys.path.append(direc) for direc in add_dir]

# Importing tasks functions
from src.tweets_ingestion import ingest_tweets
from src.tweets_etl import etl_tweets, etl_tweet_entities

AIRFLOW_EMAIL = os.environ.get("AIRFLOW_EMAIL")

default_args = {
    "owner": "ggaz",
    "depends_on_past": False,
    "start_date": datetime(2022, 3, 1),
    "email": [AIRFLOW_EMAIL, ],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=45)
}

tweets_dag = DAG(
    "twitter_tweets_dag",
    default_args=default_args,
    description="ETL DAG for tweet data in our twitter data pipeline.",
    schedule_interval="20 */4 * * *",
    tags=["twitter", ]
)

ingest_tweets_task = PythonOperator(
    task_id="twitter_tweets_ingestion",
    python_callable=ingest_tweets,
    dag=tweets_dag
)

etl_tweets_task = PythonOperator(
    task_id="twitter_tweets_etl",
    python_callable=etl_tweets,
    dag=tweets_dag
)

etl_tweets_entities_task = PythonOperator(
    task_id="twitter_tweets_entities_etl",
    python_callable=etl_tweet_entities,
    dag=tweets_dag
)

ingest_tweets_task >> [etl_tweets_task, etl_tweets_entities_task]
