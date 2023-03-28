import json
import time

from utils import STUDENT_ID, create_session, create_client

QUEUE_NAME = f"pongos_cw_sqs_queue_{STUDENT_ID}"


# Define a function that retrieves the ARN associated with an SQS queue, given its URL
def get_arn_with_url(client, url):
    # Call the get_queue_attributes method of the provided client object, passing in the provided URL and specifying that it wants the QueueArn attribute
    # Extract the QueueArn value from the 'Attributes' dictionary that is returned by the get_queue_attributes method call
    # Return the extracted QueueArn value
    return client.get_queue_attributes(QueueUrl=url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']


# Define a function that checks whether an SQS queue exists, and returns the associated ARN and URL if it does.
def queue_exists(**kwargs):
    # Get the name parameter from kwargs, or set it to None if it is not provided.
    name = kwargs.get("name", None)
    # If name is None, print an error message and return a tuple indicating that the queue does not exist.
    if not name:
        print("[-]Please provide a name for the queue...")
        return False, None, None

    # Get the client parameter from kwargs, or create a new SQS client if it is not provided.
    client = kwargs.get("client", create_client("sqs"))

    # Try to get the URL of the queue associated with the provided name.
    try:
        response = client.get_queue_url(QueueName=name)
        queue_url = response["QueueUrl"]
        # If the queue URL is retrieved successfully, return a tuple indicating that the queue exists, along with its ARN and URL.
        return True, get_arn_with_url(client, queue_url), queue_url
    # If the queue does not exist, catch the QueueDoesNotExist exception and return a tuple indicating that the queue does not exist.
    except client.exceptions.QueueDoesNotExist:
        return False, None, None


def create_queue(name, **kwargs):
    # name = kwargs.get("name", None)
    client = kwargs.get("client") or create_client("sqs")
    it_exists, arn, url = queue_exists(name=name, client=client)
    if it_exists:
        print("[+]Queue already exists, here you go :)")
        return arn, url
    response = client.create_queue(QueueName=name)
    queue_url = response['QueueUrl']
    print(f"[+]Queue {name} created with URL: {queue_url}")
    return get_arn_with_url(client, queue_url), queue_url


# Define a function that gives an S3 bucket permission to notify an SQS queue
def give_bucket_permission_to_notify(bucket_name, queue_url, queue_arn, **kwargs):
    # Get the SQS and S3 clients from kwargs, or create new clients if they are not provided
    client = kwargs.get("client") or create_client("sqs")
    s3_client = kwargs.get("s3_client") or create_client("s3")

    # Define a dictionary that represents the policy to be applied to the SQS queue
    q_policy = {
        "Version": "2012-10-17",
        "Id": "New-Allowing-Policy",
        "Statement": [
            {
                "Sid": "Allow-S3-Bucket-Send-Message",
                "Effect": "Allow",
                "Principal": {
                    "Service": "s3.amazonaws.com"
                },
                "Action": "sqs:SendMessage",
                "Resource": queue_arn,
                "Condition": {
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:s3:*:*:{bucket_name}"
                    }
                }
            }
        ]
    }

    # Apply the policy to the SQS queue by calling the set_queue_attributes method of the SQS client
    q_p_response = client.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            'Policy': json.dumps(q_policy)
        }
    )

    # Define a dictionary that represents the policy to be applied to the S3 bucket
    b_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Allow-S3-Bucket-Send-Notification",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": "s3:PutBucketNotification",
                "Resource": f"arn:aws:s3:::{bucket_name}"
            }
        ]
    }

    # Apply the policy to the S3 bucket by calling the put_bucket_policy method of the S3 client
    b_p_response = s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(b_policy)
    )

    # Return the responses from the set_queue_attributes and put_bucket_policy method calls
    return q_p_response, b_p_response

