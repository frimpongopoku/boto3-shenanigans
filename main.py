from make_ec2_instance import lets_see_security_groups, create_ec2_instance, INSTANCE_NAME
from make_s3_bucket import create_s3_bucket, BUCKET_NAME
from make_uploads import upload_images
from utils import create_session, AWS_REGION

SESSION = create_session()
if __name__ == '__main__':
    # upload_images()
    # lets_see_security_groups()
    # insta = create_ec2_instance(INSTANCE_NAME)
    client = SESSION.client("s3")
    bucket = create_s3_bucket(bucket_name=BUCKET_NAME, client=client)
    print("S3 BUCKET: ", bucket)


