import boto3

from lambdas.index import FOLDER_CONTAINING_ZIPS, U_BUCKET_NAME, TEMPLATE_PATH
from make_ec2_instance import create_ec2_instance
from make_s3_bucket import create_bucket_from_template
from utils import create_session, load_json
import os

SESSION = create_session(False)
resource = SESSION.resource('ec2')
client = SESSION.client("ec2")
s3_client = SESSION.client("s3")
formation_client = SESSION.client("cloudformation")
PEM_NAME = "my_authentication_key_pair"


def upload_zipped_content(_client, bucket_name):
    # Loop through each file in the directory
    try:
        for filename in os.listdir(FOLDER_CONTAINING_ZIPS):
            print("[..]Currently Uploading file: ", filename)
            filepath = os.path.join(FOLDER_CONTAINING_ZIPS, filename)

            with open(filepath, 'rb') as f:
                _client.upload_fileobj(f, bucket_name, filename)

            print(f"[+]{filename} uploaded to '{bucket_name}'")
        return True
    except Exception as e:
        print("[-]Error happened while uploading zips ", str(e))
        return False


def make_key_pair(name):
    key_pairs = list(resource.key_pairs.filter(Filters=[{'Name': 'key-name', 'Values': [name]}]))
    if not key_pairs:
        key_pair = resource.create_key_pair(KeyName=name)
        # Save the private key to a file
        with open(f'{name}.pem', 'w') as file:
            file.write(key_pair.key_material)
    else:
        key_pair = key_pairs[0]

    return key_pair


SECURITY_GROUP_NAME = "group_for_testing_deployment"
EC2_NAME = "elite_another_instance_to_test_theory"
make_key_pair(PEM_NAME)


def deploy():
    # Create a utility bucket that will contain any zipped files or content that will be needed to run content in
    # different parts of the application
    create_bucket_from_template(TEMPLATE_PATH, U_BUCKET_NAME, client=s3_client,
                                formation_client=formation_client)
    # Now upload all the zipped content into the utility bucket. (Items in this bucket will be referred later on)
    upload_zipped_content(s3_client, U_BUCKET_NAME)
    # Make authentication keys that will be used to access EC2 later on
    make_key_pair(PEM_NAME)
    # Now create EC2 instance
    instance = create_ec2_instance(EC2_NAME, client=client, resource_client=resource,
                                   security_group_name=SECURITY_GROUP_NAME, options={"KeyName": PEM_NAME, "UserData": '''#!/bin/bash
                                          sudo yum update
                                          sudo yum -y install python3-pip awscli
                                          sudo pip install boto3
                                         '''})

    if instance:
        print(f"[+]EC2 instance created :{instance}")


# This part is run locally!
# Then we will manually SSH into the ec2 instance and unzip the "app.zip" in our utility function
# Then start "main.py" from there
deploy()
