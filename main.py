from lambdas.index import generate_lambda_functions
from make_dynamo_db import create_table_from_template, TABLE_NAME
from make_ec2_instance import lets_see_security_groups, create_ec2_instance, INSTANCE_NAME
from make_s3_bucket import BUCKET_NAME, create_bucket_from_template, create_trigger_relationship_with_queue
from make_sqs_queue import create_queue, QUEUE_NAME
from make_uploads import upload_images
from utils import create_session, AWS_REGION, load_json

SESSION = create_session()
if __name__ == '__main__':
    # response = generate_lambda_functions(session=SESSION)
    # print("LOVELY ARN RESPONSES", response)
    # ---------- Test Notification Relationship ---------
    client = SESSION.client("s3")
    template = load_json("templates/create_s3.json")
    bucket_arn = create_bucket_from_template(template=template, client=client, bucket_name=BUCKET_NAME)
    print("BUCKET ARN: ", bucket_arn)
    client = SESSION.client("sqs")
    resource = SESSION.resource("s3")
    arn, url = create_queue(client=client, name=QUEUE_NAME)
    print("QUEUE ARN, URL ", arn, url)
    sqs_client = SESSION.client("sqs")
    create_trigger_relationship_with_queue(bucket_arn, BUCKET_NAME, arn, url, s3_resource=resource, client=sqs_client)
    # ---------------------------------------------------------------------------------
    # ------------------------------TEST BUCKET CREATION------------------------------
    # client = SESSION.client("s3")
    # template = load_json("templates/create_s3.json")
    # bucket = create_bucket_from_template(template=template,client=client, bucket_name=BUCKET_NAME)
    # print("LETS SEE THE ARN HERE", bucket)
    # ---------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------
