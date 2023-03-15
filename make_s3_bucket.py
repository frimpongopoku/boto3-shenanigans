import json
import time

from utils import create_client, create_resource, create_stack, STUDENT_ID

BUCKET_NAME = "pongoss3buckets2023351"


def bucket_exists(**kwargs):
    name = kwargs.get("bucket_name", None)
    client = kwargs.get("client", None) or create_client("s3")
    result = client.list_buckets()
    buckets = [bucket['Name'] for bucket in result['Buckets']]
    print("BUCKETS", buckets)
    is_in = name in buckets
    return is_in, name


# Remember it needs to create from cloud formation template here here....
def create_bucket_from_template(**kwargs):
    bucket_template = kwargs.get("template")
    bucket_name = kwargs.get("bucket_name")
    stack_name = f"pongos-new-s3-stack-{str(int(time.time()))}-{STUDENT_ID}"
    formation_client = kwargs.get("formation_client")
    s3_client = kwargs.get("client", create_client("s3"))
    s3_resource = create_resource("s3")

    it_exists, bucket = bucket_exists(bucket_name=bucket_name, client=s3_client)
    if it_exists:
        print(f"The bucket with name '{bucket}' already exists, here you go!")
        return s3_resource.Bucket(bucket)

    stack_id = create_stack(template=bucket_template, formation_client=formation_client, stack_name=stack_name)

    if stack_id:
        return s3_resource.Bucket(bucket_name)  # returns a reference to the bucket
    return None
