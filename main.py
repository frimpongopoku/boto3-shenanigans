from lambdas.index import generate_lambda_functions, DYNAMO_ENTRY_FUNCTION_NAME, EMAILING_FUNCTION_NAME
from lambdas.lambda_utils import create_lambda_trigger_from_sqs, create_event_source_mapping
from make_dynamo_db import create_table_from_template, TABLE_NAME, enable_streaming_on_dyno_table, empty_database_table
from make_s3_bucket import BUCKET_NAME, create_bucket_from_template, create_trigger_relationship_with_queue, \
    empty_bucket
from make_sns_topic import TOPIC_NAME, create_sns_topic, subscribe_emails_to_topic, EMAIL_LIST
from make_sqs_queue import create_queue, QUEUE_NAME
from make_uploads import upload_images
from utils import create_session, load_json, STUDENT_ID

SESSION = create_session()
EC2 = SESSION.client("ec2")
S3 = SESSION.client("s3")
LAMBDA = SESSION.client("lambda")
SNS = SESSION.client("sns")
DYNAMO = SESSION.client("dynamodb")
SQS = SESSION.client("sqs")
CLOUD_FORMATION = SESSION.client("cloudformation")
DIRECTORY = '/Users/PongoALU/Documents/CPD/images'


# The following functions in this file are just simple "grouping functions" that are used to wrap core
# Processes into steps to make the code easy to read
# @author: Frimpong Opoku Agyemang

def new_step(text):
    dashes = ""
    for i in range(len(text)):
        dashes += "-"
    print(dashes)
    print(text)
    print(dashes)



def make_s3_bucket():
    template = load_json("templates/create_s3.json")
    return create_bucket_from_template(template, BUCKET_NAME,
                                       formation_client=CLOUD_FORMATION, client=S3)


def make_dynamodb_table():
    template = load_json("templates/create_dynamodb_table.json")
    return create_table_from_template(template, TABLE_NAME, formation_client=CLOUD_FORMATION, client=DYNAMO)


def make_sqs():
    return create_queue(QUEUE_NAME, client=SQS)


def setup_relationship_between_queue_and_lambda():
    arn, url = create_queue(QUEUE_NAME, client=SQS)
    response = create_lambda_trigger_from_sqs(arn, DYNAMO_ENTRY_FUNCTION_NAME, client=LAMBDA)


def setup_relationship_between_dynamodb_table_and_emailing_lambda(stream_arn):
    return create_event_source_mapping(stream_arn, EMAILING_FUNCTION_NAME, options={"StartingPosition": 'TRIM_HORIZON'},
                                       client=LAMBDA)


def make_sns_topic_and_subscribe_emails():
    arn = create_sns_topic(TOPIC_NAME, client=SNS)
    response = subscribe_emails_to_topic(EMAIL_LIST, arn, client=SNS)
    if response:
        print(f"[+]All emails subscribed to the topic {arn}!")


def run_all_steps():
    # Step 1 - Generate s3 bucket from template
    new_step("STEP 1 - MAKE S3 FROM TEMPLATE")
    make_s3_bucket()
    # Step 2 - Create dynamodb table that is going to be used later
    new_step("STEP 2 - MAKE DYNAMO DB TABLE FROM TEMPLATE")
    table_arn = make_dynamodb_table()
    # Step 3 - Create SQS queue that will be triggered when there is a new upload in the bucket
    new_step("STEP 3 - MAKE SQS QUEUE")
    queue_arn, queue_url = make_sqs()
    # Step 4 - Setup the relationship between the bucket and the queue here
    new_step("STEP 4 - MAKE BUCKET NOTIFY QUEUE")
    create_trigger_relationship_with_queue(BUCKET_NAME, queue_arn, queue_url, s3_client=S3, client=SQS)
    # Step 5 - Generate the 2 needed lambda functions
    new_step("STEP 5 - GENERATE LAMBDA FUNCTIONS")
    generate_lambda_functions(session=SESSION)
    # Step 6 - Setup a relationship between the sqs queue and the lambda function that should be triggered on new entry
    new_step("STEP 6 - MAKE QUEUE TRIGGER LAMBDA FUNCTION")
    create_lambda_trigger_from_sqs(queue_arn, DYNAMO_ENTRY_FUNCTION_NAME, client=LAMBDA)
    # Step 7 - Enable streaming in dynamodb table
    new_step("STEP 7 - ENABLE STREAMING ON OUR DYNAMO DB TABLE")
    stream_arn = enable_streaming_on_dyno_table(TABLE_NAME, client=DYNAMO)
    # Step 8 - Now create a relationship between the dynamodb table and the second lambda function so that it can be triggered when new items are entered
    new_step("STEP 8 - MAKE DYNAMO TABLE INSERTION TRIGGER SECOND LAMBDA")
    setup_relationship_between_dynamodb_table_and_emailing_lambda(stream_arn)
    # Step 9 - Now create an SNS topic and subscribe some emails to it so that we can notify when we find pedestrians
    new_step("STEP 9 - GENERATE SNS TOPIC & SUBSCRIBE NOTIFIABLE EMAILS")
    make_sns_topic_and_subscribe_emails()

    # Now start the application (Uploading Images)...
    # ------------------------------------------------
    new_step("STEP 10 - NOW UPLOAD IMAGES")
    upload_images(BUCKET_NAME, client=S3, directory=DIRECTORY)


def reset_application():
    bucket_emptied = empty_bucket(BUCKET_NAME, S3)
    table_emptied = empty_database_table(TABLE_NAME, DYNAMO)
    new_step("INITIAL CLEANUP")

    if bucket_emptied:
        print(f"[+]Bucket '{BUCKET_NAME}' is emptied....")
    if table_emptied:
        print(f"[+]Table '{TABLE_NAME}' is emptied....")
        return bucket_emptied and table_emptied


def start_application():
    print("-----------------------------------------------------------------------------")
    print(f"AUTHOR: FRIMPONG OPOKU AGYEMANG ({STUDENT_ID}) ")
    print("-----------------------------------------------------------------------------")
    print("Choose from the following options:\nA. Run Application \nB. Exit Application")
    print("-----------------------------------------------------------------------------")
    option = input("> ")

    option = option.lower()
    if option == "a":
        is_fresh_plate = reset_application()
        if is_fresh_plate:
            run_all_steps()
        else:
            print("[+] Sorry, it looks like app could not be reset... (Check Error Logs)")
        start_application()
    elif option == "b":
        exit()
    else:
        start_application()


if __name__ == '__main__':
    start_application()