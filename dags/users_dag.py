import os
import sys
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Adding project directories for airflow
add_dir = [os.path.abspath(os.path.join(__file__, "../..")), os.path.abspath(os.path.join(__file__, "../../src")),
           os.path.abspath(os.path.join(__file__, "../../src/resources"))]
[sys.path.append(direc) for direc in add_dir]

# Importing tasks fucntions
from src.users_etl import etl_users, etl_user_metrics
from src.users_ingestion import ingest_users


AIRFLOW_EMAIL = os.environ.get("AIRFLOW_EMAIL")

default_args = {
    "owner": "ggaz",
    "depends_on_past": False,
    "start_date": datetime(2022, 3, 1),
    "email": [AIRFLOW_EMAIL, ],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=45),
}

user_dag = DAG(
    "twitter_users_dag",
    default_args=default_args,
    description="ETL DAG for user data in our twitter data pipeline.",
    schedule_interval="10 8 * * *",
    tags=["twitter", ]
)

ingest_users_task = PythonOperator(
    task_id="users_ingestion",
    python_callable=ingest_users,
    dag=user_dag
)

etl_users_task = PythonOperator(
    task_id="twitter_users_etl",
    python_callable=etl_users,
    dag=user_dag
)

etl_user_metrics_task = PythonOperator(
    task_id="twitter_user_metrics_etl",
    python_callable=etl_user_metrics,
    dag=user_dag
)


ingest_users_task >> [etl_users_task, etl_user_metrics_task]
