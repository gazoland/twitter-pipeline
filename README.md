# Twitter Data Pipeline

## Introduction

The purpose of this project is to build an ETL pipeline that will be able to extract user and tweet data from specific Twitter users using Twitter API into a Datalake built on AWS S3.
The idea is to prepare data for future internal analysis purposes.
As data is loaded into the Datalake, it will be processed and transformed into a relational format and loaded into an AWS RDS instance running a postgreSQL database.

## Project Architecture

The project is divided into two stages: 

1 - The ingestion stage: Retrieving data from the Twitter API into the Datalake; 
2 - The ETL stage: Extracting, transforming and loading the data into a RDBMS.

### 1. Ingestion

The project objective is to retrieve data from specific Twitter users who are well known in the tech industry such as Elon Musk, Jeff Bezos etc.
It will be divided into 3 parts:

1 - From each user we will gather data about their profile description, profile creation date, if they are verified users, public metrics like total tweets, total followers etc.
This information will be collected once per day.

2 - We also want collect data about all these users' tweets throughout the year of 2022 since Jan. 1st. Information about each tweet will include: content (text and entities mentioned within the text), date created, conversation id, user_id being replied to, referenced tweets and public metrics (total of likes, retweets, replies and quotes).
The tweets data will be collected every 4 hours.

3 - Since the tweets' public metrics change over time, we will need to request this information many times for the same tweets. This step will run separately from the previous one.

### 2. ETL

The ingestion stage results into 3 different data sets stored in the S3 Datalake bucket.
So there will be 3 different scripts for extracting this data, applying the necessary transformations to turn them into the desired data model and loading them into a RDBMS.

The project architecture and the technologies used are shown as follows:

![pipeline](https://user-images.githubusercontent.com/68711010/162328922-168c1e28-8b92-4961-b9cc-1d6a6181c83f.png)

## Data Model
### RDBMS Schema

![database-schema](https://user-images.githubusercontent.com/68711010/162328942-d5031a9a-5b83-4864-80c7-d3453e1e6c95.png)
