import os

from lambdas.lambda_utils import create_lambda_function
from make_s3_bucket import create_bucket_from_template
from utils import load_json, LAB_ROLE_ARN

U_BUCKET_NAME = "pongosutilitybuckets2023351"
TEMPLATE_PATH = "templates/create_my_utility_bucket.json"  # Relative to root folder
FOLDER_CONTAINING_ZIPS = "./lambdas/zips"

DYNAMO_ENTRY_FUNCTION_NAME = "functionToCreateItemsInDynamoDB"
DYNAMO_LAMBDA_ZIPPED_FILE_NAME = "dynamo_entry_function.py.zip"
DYNAMO_HANDLER_NAME = "dynamo_entry_function.lambda_handler"

EMAILING_FUNCTION_NAME = "functionToEmailIfPassengerExists"
EMAILING_LAMBDA_ZIPPED_FILE_NAME = "emailing_function.py.zip"
EMAILING_LAMBDA_HANDLER_NAME = "emailing_function.lambda_handler"


def upload_zipped_lambdas(s3_client, bucket_name):
    # Loop through each file in the directory
    try:
        for filename in os.listdir(FOLDER_CONTAINING_ZIPS):
            print("[..]Currently Uploading file: ", filename)
            filepath = os.path.join(FOLDER_CONTAINING_ZIPS, filename)

            with open(filepath, 'rb') as f:
                s3_client.upload_fileobj(f, bucket_name, filename)

            print(f"[+]{filename} uploaded to '{bucket_name}'")
        return True
    except Exception as e:
        print("[-]Error happened while uploading zips ", str(e))
        return False


def generate_lambda_functions(**kwargs):
    """
    1. We need to create the utility bucket if it doesnt exist, if it does we ignore
    2. Then upload the corresponding lambda zip files into that bucket (doesnt matter if its there or not, we should upload/overwrite everytime)
    3. And then we create the lambda function1 - for dynamo entry

    4. Then now we go ahead and create  lambda function2 - for emailing
    5. Then we set it to be triggered by the dynamo db entry, and that's all.

    :return:
    """
    session = kwargs.get("session")
    s3_client = session.client("s3")
    formation_client = session.client("cloudformation")
    template = load_json(TEMPLATE_PATH)
    create_bucket_from_template(template, U_BUCKET_NAME, client=s3_client,
                                formation_client=formation_client)
    zips_uploaded = upload_zipped_lambdas(s3_client, U_BUCKET_NAME)
    if not zips_uploaded:
        print("[-]For some reason we could not upload zipped lambda functions, please check logs...")
        return None, None

    # Now we create dynamo entry lambda
    # ----------------------------------
    code_source = {'S3Bucket': U_BUCKET_NAME, 'S3Key': DYNAMO_LAMBDA_ZIPPED_FILE_NAME}
    dyno_lambda_arn = create_lambda_function(function_name=DYNAMO_ENTRY_FUNCTION_NAME, role=LAB_ROLE_ARN,
                                             code_source=code_source, handler_name=DYNAMO_HANDLER_NAME)

    # Now we create emailing lambda
    # ----------------------------------
    code_source["S3Key"] = EMAILING_LAMBDA_ZIPPED_FILE_NAME
    email_lambda_arn = create_lambda_function(function_name=EMAILING_FUNCTION_NAME, role=LAB_ROLE_ARN,
                                              code_source=code_source, handler_name=EMAILING_LAMBDA_HANDLER_NAME)
    return dyno_lambda_arn, email_lambda_arn
