import boto3
import os
import time
from dotenv import load_dotenv
from utils import create_session
load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SESSION = create_session()
SECONDS_TO_WAIT = 15
# Set the directory containing the images to be uploaded
DIRECTORY = '/Users/PongoALU/Documents/CPD/images'

# Initialize the S3 client
S3 = SESSION.client('s3')


def upload_images():
    # Loop through each file in the directory
    for filename in os.listdir(DIRECTORY):
        print("Current File: ", filename)
        # Construct the full path to the file
        filepath = os.path.join(DIRECTORY, filename)

        # Wait for 30 seconds before uploading the file
        time.sleep(SECONDS_TO_WAIT)

        # Upload the file to the S3 bucket
        with open(filepath, 'rb') as f:
            S3.upload_fileobj(f, BUCKET_NAME, filename)

        print(f"{filename} uploaded to S3")
