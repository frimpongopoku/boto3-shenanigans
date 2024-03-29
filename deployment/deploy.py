import boto3

from utils import create_session, LAB_ROLE_ARN

ZIPPED_FOLDER_NAME = "dummy.py.zip"
SOURCE_CODE_ZIP_IN_BUCKET = f"s3://pongosutilitybuckets2023351/{ZIPPED_FOLDER_NAME}"
LAB_ROLE_PROFILE_ARN = "arn:aws:iam::122802082660:instance-profile/LabInstanceProfile"

region_name="us-east-1"
# --------------------------------------------------------------------------------------------------------
# Set up EC2 resource
SESSION = create_session()
ec2 = SESSION.resource('ec2')
client = SESSION.client("ec2")

AMI_IMAGE_ID = 'ami-02f3f602d23f1659d'
PEM_NAME = "my_authentication_key_pair"

# Create a key pair
# key_pair = ec2.create_key_pair(KeyName=PEM_NAME)
key_pair_name = 'your_key_pair_name'
key_pairs = list(ec2.key_pairs.filter(Filters=[{'Name': 'key-name', 'Values': [PEM_NAME]}]))
if not key_pairs:
    key_pair = ec2.create_key_pair(KeyName=PEM_NAME)
    # Save the private key to a file
    with open(f'{PEM_NAME}.pem', 'w') as file:
        file.write(key_pair.key_material)
else:
    key_pair = key_pairs[0]

# Set up security group
SECURITY_GROUP_NAME = "group_for_testing_deployment"
response = client.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [SECURITY_GROUP_NAME]}])

if not response['SecurityGroups']:
    security_group = ec2.create_security_group(GroupName=SECURITY_GROUP_NAME,
                                               Description='Security group for your Python app')
    # Add rules to security group
    security_group.authorize_ingress(IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0')  # SSH access
    security_group.authorize_ingress(IpProtocol='tcp', FromPort=80, ToPort=80, CidrIp='0.0.0.0/0')  # HTTP access
else:
    security_group = ec2.SecurityGroup(response['SecurityGroups'][0]['GroupId'])


# Launch EC2 instance with the existing IAM role (labRole)
instance = ec2.create_instances(ImageId=AMI_IMAGE_ID,
                                InstanceType='t2.micro',
                                KeyName=PEM_NAME,
                                MinCount=1,
                                MaxCount=1,
                                SecurityGroupIds=[security_group.id],
                                IamInstanceProfile={'Arn': LAB_ROLE_PROFILE_ARN},
                                UserData=f'''#!/bin/bash
                                            sudo yum update
                                            sudo yum -y install python3-pip awscli
                                            sudo pip install boto3
                                            aws s3 cp {SOURCE_CODE_ZIP_IN_BUCKET} .
                                            unzip {ZIPPED_FOLDER_NAME}
                                            sudo python3 dummy.py &
                                            '''
                                , TagSpecifications=[
        {'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': "ec2_for_testing_deployment"}, ]}, ]
                                )[0]

# Wait for the instance to be in the 'running' state
instance.wait_until_running()

# Get the public DNS name of the instance
instance_dns = instance.public_dns_name
print("SEE HERE", instance)
print('Your Python application is running at:', instance_dns)
