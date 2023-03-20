import os

from lambdas.lambda_utils import create_lambda_function
from utils import LAB_ROLE_ARN

U_BUCKET_NAME = "pongosutilitybuckets2023351"
TEMPLATE_PATH = "templates/create_my_utility_bucket.json"  # Relative to root folder
FOLDER_CONTAINING_ZIPS = "./../zips" # Relative to deployment folder

DYNAMO_ENTRY_FUNCTION_NAME = "functionToCreateItemsInDynamoDB"
DYNAMO_LAMBDA_ZIPPED_FILE_NAME = "dynamo_entry_function.py.zip"
DYNAMO_HANDLER_NAME = "dynamo_entry_function.lambda_handler"

EMAILING_FUNCTION_NAME = "functionToEmailIfPassengerExists"
EMAILING_LAMBDA_ZIPPED_FILE_NAME = "emailing_function.py.zip"
EMAILING_LAMBDA_HANDLER_NAME = "emailing_function.lambda_handler"

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
