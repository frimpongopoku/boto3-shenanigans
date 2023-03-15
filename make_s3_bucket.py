import json
import time

from utils import STUDENT_ID, create_session, create_client, create_resource

# The name of the instance to be created
# BUCKET_NAME = f"pongos_s3_bucket_{time.time()}_{STUDENT_ID}"

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
    template = kwargs.get("template")
    bucket_name = kwargs.get("bucket_name")
    stack_name = kwargs.get("stack_name", "pongos-new-stack-" + str(int(time.time())))
    if not template:
        print("Please provide a json cloud formation template to be used...")
        return None
    formation_client = create_client("cloudformation")
    s3_client = create_client("s3")
    s3_resource = create_resource("s3")
    it_exists, bucket = bucket_exists(bucket_name=bucket_name, client=s3_client)
    if it_exists:
        print(f"The bucket with name '{bucket}' already exists, here you go!")
        return s3_resource.Bucket(bucket)

    stack_response = formation_client.create_stack(
        StackName=stack_name,
        TemplateBody=json.dumps(template)
    )
    stack_id = stack_response.get('StackId')
    formation_client.get_waiter('stack_create_complete').wait(
        StackName=stack_id)  # We wait for the stack to be created before moving on
    print(f"Stack created with ID '{stack_id}'...")

    return s3_resource.Bucket(bucket_name) # returns a reference to the bucket
