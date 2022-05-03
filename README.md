# Twitter Data Pipeline

## Introduction

The purpose of this project is to build an ETL pipeline that will be able to extract user and tweet data from specific Twitter users using Twitter API into a Datalake built on AWS S3.
The idea is to prepare data for future internal analysis purposes.
As data is loaded into the Datalake, it will be processed and transformed into a relational format and loaded into an AWS RDS instance running a postgreSQL database.

## Project Architecture

The project is divided into two stages: 

- The ingestion stage: Retrieving data from the Twitter API into the Datalake; 

- The ETL stage: Extracting, transforming and loading the data into a RDBMS.

### 1. Ingestion

The project objective is to retrieve data from specific Twitter users who are well known in the tech industry such as Elon Musk, Jeff Bezos etc.
It will be divided into 3 parts:

1 - From each user we will gather data about their profile description, profile creation date, if they are verified users, public metrics like total tweets, total followers etc.
This information will be collected once per day.

2 - We also want collect data about all these users' tweets throughout the year of 2022 since Jan. 1st. Information about each tweet will include: content (text and entities mentioned within the text), date created, conversation id, user_id being replied to, referenced tweets and public metrics (total of likes, retweets, replies and quotes).
The tweets data will be collected every 4 hours.

3 - Since the tweets' public metrics change over time, we will need to request this information many times for the same tweets. This step will run separately from the previous one, every 2 hours.

### 2. ETL

The ingestion stage results into 3 different data sets stored in the S3 Datalake bucket.
So there will be 3 different scripts for extracting this data, applying the necessary transformations to turn them into the desired data model and loading them into a RDBMS.

The project architecture and the technologies used are shown as follows:

![new-pipeline](https://user-images.githubusercontent.com/68711010/165172954-04086660-287b-4a1f-ad66-eb3e013d5401.png)

## Technologies

**Python**: all scripts, as well as the Airflow Dags will be written in Python. Requests to the Twitter API will be made with the requests library (Bearer Token needed).

**AWS**: will provide all the required cloud infrastructure. Services used include:

- EC2: one instance will be hosting Apache Airflow;

-	S3: a bucket will serve as the Datalake;

-	RDS: one instance will host the RDBMS used;

-	LakeFormation: for helping in the creation of the Datalake;

-	Glue: crawlers will be used for mapping the data and creating a metastore;

-	boto3: AWS Software Development Kit for Python (Access Key ID and Secret Access Key needed).

**PostgreSQL**: the chosen RDBMS. Access from Python using psycopg2.

**Apache Airflow**: orchestration duties.

**Docker**: for easy setup configurations.

- Airflow uses DAGs to execute tasks. The tasks are divided into 3 data groups: users, tweets and tweets metrics.

![dags](https://user-images.githubusercontent.com/68711010/163054608-c4892c31-351c-49cd-b7d4-638fce19008e.png)

## Data Model

Transformed data will be in Star Schema.

### RDBMS Schema

![database-schema](https://user-images.githubusercontent.com/68711010/162328942-d5031a9a-5b83-4864-80c7-d3453e1e6c95.png)

- Future additions will include a Rest API for adding new Twitter users to the list and integrate it with functions on AWS Lambda.
