import os

from lambdas.lambda_utils import create_lambda_function
from make_s3_bucket import create_bucket_from_template
from utils import load_json, LAB_ROLE_ARN

U_BUCKET_NAME = "pongosutilitybuckets2023351"
TEMPLATE_PATH = "templates/create_my_utility_bucket.json"  # Relative to root folder
FOLDER_CONTAINING_ZIPS = "./lambdas/zips"

DYNAMO_ENTRY_FUNCTION_NAME = "functionToCreateItemsInDynamoDB"
DYNAMO_LAMBDA_ZIPPED_FILE_NAME = "dynamo_entry_lambda.zip"

EMAILING_FUNCTION_NAME = "functionToEmailIfPassengerExists"
EMAILING_LAMBDA_ZIPPED_FILE_NAME = "emailing_lambda.zip"


def upload_zipped_lambdas(s3_client, bucket_name):
    # Loop through each file in the directory
    try:
        for filename in os.listdir(FOLDER_CONTAINING_ZIPS):
            print("New Uploading file: ", filename)
            filepath = os.path.join(FOLDER_CONTAINING_ZIPS, filename)

            with open(filepath, 'rb') as f:
                s3_client.upload_fileobj(f, bucket_name, filename)

            print(f"{filename} uploaded to {bucket_name}")
        return True
    except Exception as e:
        print("Error happened while uploading zips ", str(e))
        return False


def generate_lambda_functions(**kwargs):
    """
    1. We need to create the utility bucket if it doesnt exist, if it does we ignore
    2. Then upload the corresponding lambda zip files into that bucket (doesnt matter if its there or not, we should upload everytime)
    And then we create the lambda function for dynamo entry
    Then we  set it to be triggered by the SQS we know exists already

    Then now we go ahead and create the lambda function for emailing
    Then we set it to be triggered by the dynamo db entry, and that's all.

    :return:
    """
    session = kwargs.get("session")
    s3_client = session.client("s3")
    formation_client = session.client("cloudformation")
    template = load_json(TEMPLATE_PATH)
    u_bucket = create_bucket_from_template(template=template, client=s3_client, bucket_name=U_BUCKET_NAME,
                                           formation_client=formation_client)
    zips_uploaded = upload_zipped_lambdas(s3_client, u_bucket.name)
    if not zips_uploaded:
        print("For some reason we could not upload zipped lambda functions, please check logs...")
        return None, None

    # Now we create dynamo entry lambda
    # ----------------------------------
    code_source = {'S3Bucket': u_bucket.name, 'S3Key': DYNAMO_LAMBDA_ZIPPED_FILE_NAME}
    dyno_lambda_arn = create_lambda_function(function_name=DYNAMO_ENTRY_FUNCTION_NAME, role=LAB_ROLE_ARN,
                                             code_source=code_source)

    # Now we create emailing lambda
    # ----------------------------------
    code_source["S3Key"] = EMAILING_LAMBDA_ZIPPED_FILE_NAME
    email_lambda_arn = create_lambda_function(function_name=EMAILING_FUNCTION_NAME, role=LAB_ROLE_ARN,
                                              code_source=code_source)
    return dyno_lambda_arn, email_lambda_arn
