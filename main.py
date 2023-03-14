from make_ec2_instance import lets_see_security_groups, create_ec2_instance, INSTANCE_NAME
from make_s3_bucket import BUCKET_NAME, create_bucket_from_template
from make_sqs_queue import create_queue, QUEUE_NAME
from make_uploads import upload_images
from utils import create_session, AWS_REGION, load_json

SESSION = create_session()
if __name__ == '__main__':
    # upload_images()
    # lets_see_security_groups()
    # insta = create_ec2_instance(INSTANCE_NAME)
    # client = SESSION.client("s3")
    # bucket = create_s3_bucket(bucket_name=BUCKET_NAME, client=client)
    # client = SESSION.client("sqs")
    # q = create_queue(name =QUEUE_NAME)
    # bucket = create_bucket_from_template(template=)
    template = load_json("./templates/create_s3.json")
    bucket = create_bucket_from_template(template=template, bucket_name=BUCKET_NAME)
    print("HERE IS YOUR BUCKET: ", bucket)
