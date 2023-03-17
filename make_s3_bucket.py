import json
import time

from make_sqs_queue import give_bucket_permission_to_notify
from utils import create_client, create_resource, create_stack, STUDENT_ID

BUCKET_NAME = "pongoss3buckets2023351"


def get_bucket_arn(bucket_name, **kwargs):
    client = kwargs.get("client")
    sts = kwargs.get("sts_client", create_client("sts"))
    response = client.get_bucket_location(Bucket=bucket_name)
    bucket_region = response['LocationConstraint'] or 'us-east-1'
    account_id = sts.get_caller_identity().get('Account')
    bucket_arn = f'arn:aws:s3:{bucket_region}:{account_id}:{bucket_name}'
    return bucket_arn


def bucket_exists(**kwargs):
    name = kwargs.get("bucket_name", None)
    client = kwargs.get("client", None) or create_client("s3")
    result = client.list_buckets()
    buckets = [bucket['Name'] for bucket in result['Buckets']]
    print("BUCKETS", buckets)
    is_in = name in buckets
    return is_in, name


def create_bucket_from_template(bucket_template, bucket_name, **kwargs):
    # bucket_template = kwargs.get("template")
    # bucket_name = kwargs.get("bucket_name")
    stack_name = f"pongos-new-s3-stack-{str(int(time.time()))}-{STUDENT_ID}"
    formation_client = kwargs.get("formation_client")
    s3_client = kwargs.get("client", create_client("s3"))
    # s3_resource = create_resource("s3")

    it_exists, bucket = bucket_exists(bucket_name=bucket_name, client=s3_client)
    if it_exists:
        print(f"The bucket with name '{bucket}' already exists, here you go!")
        # return s3_resource.Bucket(bucket).arn
        return get_bucket_arn(bucket_name, client=s3_client)
        # return f"arn:aws:s3:::{bucket_name}"

    stack_id = create_stack(template=bucket_template, formation_client=formation_client, stack_name=stack_name)

    if stack_id:
        # return s3_resource.Bucket(bucket_name).arn  # returns a reference to the bucket
        return get_bucket_arn(bucket_name, client=s3_client)
        # return f"arn:aws:s3:::{bucket_name}"
    return None


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
    s3_client = kwargs.get("s3_client", create_client("s3"))
    sqs_client = kwargs.get("client")  # sqs client
    give_bucket_permission_to_notify(bucket_name, queue_url, queue_arn, client=sqs_client, s3_client=s3_client)
    config = {"QueueConfigurations": [{'QueueArn': queue_arn, 'Events': ['s3:ObjectCreated:*']}]}
    try:
        response = s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=config
        )
        print(f"Awesome! Your queue will now receive notifications when items are uploaded into '{bucket_name}'.")
        return response
    except Exception as e:
        print(f"An error occurred while setting up the bucket notification configuration: {e}")
        return None
