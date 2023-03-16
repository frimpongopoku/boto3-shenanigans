from lambdas.index import generate_lambda_functions, DYNAMO_ENTRY_FUNCTION_NAME, EMAILING_FUNCTION_NAME
from lambdas.lambda_utils import create_lambda_trigger_from_sqs, create_event_source_mapping
from make_dynamo_db import create_table_from_template, TABLE_NAME, enable_streaming_on_dyno_table
from make_ec2_instance import lets_see_security_groups, create_ec2_instance, INSTANCE_NAME
from make_s3_bucket import BUCKET_NAME, create_bucket_from_template, create_trigger_relationship_with_queue
from make_sns_topic import TOPIC_NAME, create_sns_topic, subscribe_emails_to_topic, EMAIL_LIST
from make_sqs_queue import create_queue, QUEUE_NAME
from make_uploads import upload_images
from utils import create_session, AWS_REGION, load_json

SESSION = create_session()


def test_lambda_creation():
    # Testing the entire lambda creation process
    response = generate_lambda_functions(session=SESSION)
    print("LOVELY ARN RESPONSES", response)


def test_relationship_between_bucket_and_queue():
    client = SESSION.client("s3")
    template = load_json("templates/create_s3.json")
    bucket_arn = create_bucket_from_template(template=template, client=client, bucket_name=BUCKET_NAME)
    print("BUCKET ARN: ", bucket_arn)
    client = SESSION.client("sqs")
    resource = SESSION.resource("s3")
    arn, url = create_queue(client=client, name=QUEUE_NAME)
    print("QUEUE ARN, URL ", arn, url)
    sqs_client = SESSION.client("sqs")
    create_trigger_relationship_with_queue(BUCKET_NAME, arn, url, s3_resource=resource, client=sqs_client)


def test_relationship_between_queue_and_lambda():
    client = SESSION.client("sqs")
    l_client = SESSION.client("lambda")
    arn, url = create_queue(QUEUE_NAME, client=client)
    response = create_lambda_trigger_from_sqs(arn, DYNAMO_ENTRY_FUNCTION_NAME, client=l_client)


def test_creating_bucket_from_template():
    client = SESSION.client("s3")
    template = load_json("templates/create_s3.json")
    bucket = create_bucket_from_template(template=template, client=client, bucket_name=BUCKET_NAME)
    print("LETS SEE THE ARN HERE", bucket)


def test_creating_sqs_queue():
    client = SESSION.client("sqs")
    arn, url = create_queue(QUEUE_NAME, client=client)
    print("Response Info for QUEUE", arn, url)


def test_enabling_table_streaming():
    client = SESSION.client("dynamodb")
    response = enable_streaming_on_dyno_table(TABLE_NAME, client=client)
    print("RESPONSE AFTER STREAMING: ", response)


def test_creating_trigger_for_emailing_lambda():
    client = SESSION.client("dynamodb")
    lambda_client = SESSION.client("lambda")
    stream_arn = enable_streaming_on_dyno_table(TABLE_NAME, client=client)
    print("WE GAT THE STREAM ARN HERE: ", stream_arn)

    response = create_event_source_mapping(stream_arn, EMAILING_FUNCTION_NAME,
                                           options={"StartingPosition": 'TRIM_HORIZON'}, client=lambda_client)
    print("LOVELY TRIGGER VICTORY: ", response)


def test_creating_sns_topic():
    client = SESSION.client("sns")
    arn = create_sns_topic(TOPIC_NAME, client=client)

    print("GREAT TOPIC ARN: ", arn)

    response = subscribe_emails_to_topic(EMAIL_LIST, arn, client=client)
    if response:
        print("All emails subscribed!")


if __name__ == '__main__':
    # test_lambda_creation()
    # ---------- Test Notification to SQS Relationship ---------
    # test_relationship_between_bucket_and_queue()
    # ---------------------------------------------------------------------------------
    # ------------------------------TEST BUCKET CREATION------------------------------
    # So I am going to create the bucket
    # Then I create an sqs
    # Then I establish the relationship between them and specify permissions
    # test_creating_bucket_from_template()
    # test_creating_sqs_queue()
    # test_relationship_between_bucket_and_queue()
    # ---------------------------------------------------------------------------------
    # ------------------------------ TEST CREATING TRIGGER FROM SQS TO LAMBDA --------------------------------------------
    # Set up relationship to trigger lambda function by setting up event source mapping
    # test_relationship_between_queue_and_lambda()

    # test_enabling_table_streaming()

    # test_creating_trigger_for_emailing_lambda()
    test_creating_sns_topic()