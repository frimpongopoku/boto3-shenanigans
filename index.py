import boto3
import os
import time
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)
# Set the directory containing the images to be uploaded
directory = '/Users/PongoALU/Documents/CPD/images'

# Set the name of the S3 bucket to upload the images to
bucket_name = 'testingimagesupload0823'

# Initialize the S3 client
s3 = session.client('s3')
# s3 = boto3.client('s3')


def upload_images():
    # Loop through each file in the directory
    for filename in os.listdir(directory):
        print("Current File: ", filename)
        # Construct the full path to the file
        filepath = os.path.join(directory, filename)

        # Wait for 30 seconds before uploading the file
        time.sleep(30)

        # Upload the file to the S3 bucket
        with open(filepath, 'rb') as f:
            s3.upload_fileobj(f, bucket_name, filename)

        print(f"{filename} uploaded to S3")
