from lambdas.index import generate_lambda_functions
from make_dynamo_db import create_table_from_template, TABLE_NAME
from make_ec2_instance import lets_see_security_groups, create_ec2_instance, INSTANCE_NAME
from make_s3_bucket import BUCKET_NAME, create_bucket_from_template
from make_sqs_queue import create_queue, QUEUE_NAME
from make_uploads import upload_images
from utils import create_session, AWS_REGION, load_json

SESSION = create_session()
if __name__ == '__main__':
    response = generate_lambda_functions(session=SESSION)
    print("LOVELY ARN RESPONSES", response)
