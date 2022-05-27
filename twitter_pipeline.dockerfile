# Base image from ubuntu
FROM ubuntu:20.04

# Install python3
RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y

# Create working directory for the container
WORKDIR /twitter-pipeline

# Port which will run Airflow
ARG AIRFLOW_PORT=8080
ENV AIRFLOW_PORT=$AIRFLOW_PORT
EXPOSE $AIRLFLOW_PORT

# Airflow home
ARG AIRFLOW_HOME=./airflow
ENV AIRFLOW_HOME=$AIRFLOW_HOME

# Copy requirements.txt into the working directory
COPY requirements.txt .

# Copy original folders into the container folders
COPY ./dags ./dags
COPY ./src ./src

# Copy airflow config file into container
COPY ./airflow_home ./airflow

# Install dependencies
RUN pip3 install -r requirements.txt