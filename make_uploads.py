import os
import time
from utils import create_client

SECONDS_TO_WAIT = 30  # TODO: change this to 30 before submission


def upload_images(bucket_name, **kwargs):
    client = kwargs.get("client") or create_client("s3")
    directory = kwargs.get("directory")
    # Loop through each file in the directory
    for filename in os.listdir(directory):
        print(f"[..]Currently uploading file '{filename}'")
        # Construct the full path to the file
        filepath = os.path.join(directory, filename)

        # Wait for 30 seconds before uploading the file
        time.sleep(SECONDS_TO_WAIT)

        # Upload the file to the S3 bucket
        with open(filepath, 'rb') as f:
            client.upload_fileobj(f, bucket_name, filename)
        print(f"[+]Uploaded {filename} to S3!")
