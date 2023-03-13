from dotenv import load_dotenv
import boto3
import os

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def create_session():
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_REGION
    )
    return session
