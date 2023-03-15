import time

from dotenv import load_dotenv
import boto3
import os
import json

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

STUDENT_ID = "s2023351"
LAB_ROLE_ARN = "arn:aws:iam::122802082660:role/LabRole"


def create_session():
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_REGION
    )
    return session


def create_client(name):
    session = create_session()
    return session.client(name)


def create_resource(resource):
    session = create_session()
    return session.resource(resource)


def load_json(file_name):
    data = {}
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def create_stack(**kwargs):
    stack_name = kwargs.get("stack_name", "pongos-new-stack-" + str(int(time.time())))
    formation_client = kwargs.get("formation_client") or create_client("cloudformation")
    template = kwargs.get("template")
    if not template:
        print("Please provide a JSON cloud formation template to create your stack... :(")

    print(f"Currently creating stack '{stack_name}'...")
    stack_response = formation_client.create_stack(
        StackName=stack_name,
        TemplateBody=json.dumps(template)
    )
    stack_id = stack_response.get('StackId')
    formation_client.get_waiter('stack_create_complete').wait(
        StackName=stack_id)  # We wait for the stack to be created before moving on
    print(f"Stack created with ID '{stack_id}'...")
    return stack_id
