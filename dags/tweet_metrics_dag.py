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
from src.tweet_metrics_ingestion import ingest_tweet_metrics
from src.tweet_metrics_etl import etl_tweet_metrics

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

tweet_metrics_dag = DAG(
    "twitter_tweet_metrics_dag",
    default_args=default_args,
    description="ETL DAG for tweet metrics data in our twitter data pipeline.",
    schedule_interval=timedelta(days=1),
    tags=["twitter", ]
)

ingest_tweet_metrics_task = PythonOperator(
    task_id="twitter_tweet_metrics_ingestion",
    python_callable=ingest_tweet_metrics,
    dag=tweet_metrics_dag
)

etl_tweet_metrics_task = PythonOperator(
    task_id="twitter_tweet_metrics_etl",
    python_callable=etl_tweet_metrics,
    dag=tweet_metrics_dag
)

ingest_tweet_metrics_task >> etl_tweet_metrics_task
