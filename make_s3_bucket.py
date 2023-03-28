import json
import time

from make_sqs_queue import give_bucket_permission_to_notify
from utils import create_client, create_resource, create_stack, STUDENT_ID

BUCKET_NAME = "pongoss3buckets2023351"


# Define a function to delete all objects in an S3 bucket
def empty_bucket(bucket_name, client):
    # Check if the bucket exists
    exists, _ = bucket_exists(bucket_name, client)
    # If the bucket does not exist, return True
    if not exists:
        return True
    # List objects in the bucket
    response = client.list_objects_v2(Bucket=bucket_name)
    # Check if there are any objects
    if "Contents" not in response:
        print("[+]The bucket is already empty.")
        return True
    # Delete all objects in the bucket
    for obj in response["Contents"]:
        client.delete_object(Bucket=bucket_name, Key=obj["Key"])
    # Return True after all objects are deleted
    return True


# Define a function to get the ARN of an S3 bucket
def get_bucket_arn(bucket_name, **kwargs):
    # Get the S3 and STS clients from kwargs or create them
    client = kwargs.get("client")
    sts = kwargs.get("sts_client") or create_client("sts")
    # Get the bucket location
    response = client.get_bucket_location(Bucket=bucket_name)
    # Get the bucket region, default to 'us-east-1' if not present
    bucket_region = response['LocationConstraint'] or 'us-east-1'
    # Get the AWS account ID
    account_id = sts.get_caller_identity().get('Account')
    # Build and return the bucket ARN
    bucket_arn = f'arn:aws:s3::{bucket_region}:{account_id}:{bucket_name}'
    return bucket_arn


# Define a function to check if an S3 bucket exists
def bucket_exists(name, client):
    # List all buckets
    result = client.list_buckets()
    # Get the bucket names
    buckets = [bucket['Name'] for bucket in result['Buckets']]
    # Check if the given bucket name is in the list
    is_in = name in buckets
    # Return True and the name if the bucket exists, otherwise False and the name
    return is_in, name


# Define a function to create an S3 bucket using a CloudFormation template
def create_bucket_from_template(bucket_template, bucket_name, **kwargs):
    # Generate a unique stack name based on current time and student ID
    stack_name = f"pongos-new-s3-stack-{str(int(time.time()))}-{STUDENT_ID}"
    # Get the CloudFormation and S3 clients from kwargs or create them
    formation_client = kwargs.get("formation_client")
    s3_client = kwargs.get("client") or create_client("s3")

    # Check if the bucket exists
    it_exists, bucket = bucket_exists(bucket_name, s3_client)
    # If the bucket exists, print a message and return its ARN
    if it_exists:
        print(f"[+]The bucket with name '{bucket}' already exists, here you go!")
        return get_bucket_arn(bucket_name, client=s3_client)

    # Create a CloudFormation stack with the bucket template
    stack_id = create_stack(template=bucket_template, formation_client=formation_client, stack_name=stack_name)

    # If the stack creation is successful, return the bucket ARN
    if stack_id:
        return get_bucket_arn(bucket_name, client=s3_client)
    # If the stack creation fails, return None
    return None


# Define a function to create a trigger relationship between an S3 bucket and an SQS queue
def create_trigger_relationship_with_queue(bucket_name, queue_arn, queue_url, **kwargs):
    """
    Creates the relationship between a given s3 bucket, and a queue that should be triggered
    when a new item is uploaded
    :param queue_url:
    :param bucket_name:
    :param queue_arn:
    :param kwargs:
    :return:
    """
    # Get the S3 and SQS clients from kwargs or create them
    s3_client = kwargs.get("s3_client") or create_client("s3")
    sqs_client = kwargs.get("client")
    # Give the bucket permission to notify the queue
    give_bucket_permission_to_notify(bucket_name, queue_url, queue_arn, client=sqs_client, s3_client=s3_client)
    # Configure the bucket to send notifications to the queue
    config = {"QueueConfigurations": [{'QueueArn': queue_arn, 'Events': ['s3:ObjectCreated:*']}]}
    try:
        # Set the bucket notification configuration
        response = s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=config
        )
        # Print a success message
        print(f"[+]Awesome! Your queue will now receive notifications when items are uploaded into '{bucket_name}'.")
        return response
    except Exception as e:
        # Print an error message if an exception occurs
        print(f"[-]An error occurred while setting up the bucket notification configuration: {e}")
        return None
