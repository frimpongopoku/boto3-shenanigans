from lambdas.index import generate_lambda_functions, DYNAMO_ENTRY_FUNCTION_NAME
from lambdas.lambda_utils import create_lambda_trigger_from_sqs
from make_dynamo_db import create_table_from_template, TABLE_NAME
from make_ec2_instance import lets_see_security_groups, create_ec2_instance, INSTANCE_NAME
from make_s3_bucket import BUCKET_NAME, create_bucket_from_template, create_trigger_relationship_with_queue
from make_sqs_queue import create_queue, QUEUE_NAME
from make_uploads import upload_images
from utils import create_session, AWS_REGION, load_json

SESSION = create_session()


def test_lambda_creation():
    # Testing the entire lambda creation process
    response = generate_lambda_functions(session=SESSION)
    print("LOVELY ARN RESPONSES", response)


if __name__ == '__main__':
    test_lambda_creation()
    # ---------- Test Notification to SQS Relationship ---------
    # client = SESSION.client("s3")
    # template = load_json("templates/create_s3.json")
    # bucket_arn = create_bucket_from_template(template=template, client=client, bucket_name=BUCKET_NAME)
    # print("BUCKET ARN: ", bucket_arn)
    # client = SESSION.client("sqs")
    # resource = SESSION.resource("s3")
    # arn, url = create_queue(client=client, name=QUEUE_NAME)
    # print("QUEUE ARN, URL ", arn, url)
    # sqs_client = SESSION.client("sqs")
    # create_trigger_relationship_with_queue(BUCKET_NAME, arn, url, s3_resource=resource, client=sqs_client)
    # ---------------------------------------------------------------------------------
    # ------------------------------TEST BUCKET CREATION------------------------------
    # client = SESSION.client("s3")
    # template = load_json("templates/create_s3.json")
    # bucket = create_bucket_from_template(template=template,client=client, bucket_name=BUCKET_NAME)
    # print("LETS SEE THE ARN HERE", bucket)
    # ---------------------------------------------------------------------------------
    # ------------------------------ TEST CREATING TRIGGER FROM SQS TO LAMBDA --------------------------------------------
    # Set up relationship to trigger lambda function by setting up event source mapping
    # client = SESSION.client("sqs")
    # l_client = SESSION.client("lambda")
    # arn, url = create_queue(QUEUE_NAME, client=client)
    # response = create_lambda_trigger_from_sqs(arn, DYNAMO_ENTRY_FUNCTION_NAME, client=l_client)
