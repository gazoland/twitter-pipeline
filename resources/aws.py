import boto3
import os

ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_BUCKET = os.environ.get("S3_DATALAKE_BUCKET")


def upload_to_s3(filename, path):
    session = boto3.Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY,
                            region_name="us-east-1")
    s3 = session.resource("s3")
    s3.meta.client.upload_file(os.path.join(os.getcwd(), filename), S3_BUCKET, path + filename)
