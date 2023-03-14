import time

from utils import STUDENT_ID, create_session

# The name of the instance to be created
BUCKET_NAME = f"pongos_s3_bucket_{time.time()}_{STUDENT_ID}"


def create_client():
    session = create_session()
    return session.client('s3')


def bucket_exists(**kwargs):
    name = kwargs.get("bucket_name", None)
    client = kwargs.get("client", None) or create_client()
    result = client.list_buckets()
    buckets = [bucket['Name'] for bucket in result['Buckets']]
    # print(result)
    print("BUCKETS", buckets)
    is_in = name in buckets
    return is_in, client.Bucket(name) if is_in else None


# Remember it needs to create from cloud formation template here here....
def create_s3_bucket(**kwargs):
    bucket_name = kwargs.get("bucket_name", None)
    if not bucket_name:
        print("You need to provide a bucket name to create...")
        return None
    client = kwargs.get("client", None) or create_client()
    region = kwargs.get("region", None)
    it_exists, bucket = bucket_exists(bucket_name=bucket_name, client=client)
    if it_exists:
        print(f"The bucket with name '{bucket_name}' already exists :)")
        return bucket
    print(f"Currently creating s3 bucket '{bucket_name}'...")
    client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
    _bucket = client.Bucket(bucket_name)
    return _bucket
