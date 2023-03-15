import json
import time

from utils import STUDENT_ID, create_session, create_client

QUEUE_NAME = f"pongos_sqs_queue_{STUDENT_ID}"


def get_arn_with_url(client, url):
    return client.get_queue_attributes(QueueUrl=url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']


def queue_exists(**kwargs):
    name = kwargs.get("name", None)
    if not name:
        print("Please provide a name for the queue...")
        return False, None, None
    client = kwargs.get("client", create_client("sqs"))
    try:
        response = client.get_queue_url(QueueName=name)
        queue_url = response["QueueUrl"]
        return True, get_arn_with_url(client, queue_url), queue_url
    except client.exceptions.QueueDoesNotExist:
        return False, None, None


def create_queue(**kwargs):
    name = kwargs.get("name", None)
    client = kwargs.get("client", create_client("sqs"))
    it_exists, arn, url = queue_exists(name=name, client=client)
    if it_exists:
        print("Queue already exists, here you go :)")
        return arn, url
    response = client.create_queue(QueueName=name)
    queue_url = response['QueueUrl']
    print(f"Queue {name} created with URL: {queue_url}")
    return get_arn_with_url(client, queue_url), queue_url


def give_bucket_permission_to_notify(bucket_name, queue_url, queue_arn, **kwargs):
    client = kwargs.get("client", create_client("sqs"))
    s3_client = kwargs.get("s3_client", create_client("s3"))
    q_policy = {
        "Version": "2012-10-17",
        "Id": "New-Allowing-Policy",
        "Statement": [
            {
                "Sid": "Allow-S3-Bucket-Send-Message",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
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

    q_p_response = client.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            'Policy': json.dumps(q_policy)
        }
    )

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

    b_p_response = s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(b_policy)
    )

    return q_p_response, b_p_response
