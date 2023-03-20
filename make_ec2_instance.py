import boto3

from utils import STUDENT_ID, create_session

# The name of the instance to be created
INSTANCE_NAME = "pongos_assignment_ec2_" + STUDENT_ID

# Amazon Linux 2 Image ID
AMI_IMAGE_ID = 'ami-02f3f602d23f1659d'

# Lab Role Profile ARN
LAB_ROLE_PROFILE_ARN = "arn:aws:iam::122802082660:instance-profile/LabInstanceProfile"

SESSION = create_session()
EC2_CLIENT = SESSION.client('ec2')


def create_security_group(name, client, resource_client):
    # client = kwargs.get("client")
    # resource_client = kwargs.get("resource_client")
    response = client.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [name]}])

    if not response['SecurityGroups']:
        security_group = resource_client.create_security_group(GroupName=name)
        # Add rules to security group
        security_group.authorize_ingress(IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0')  # SSH access
        security_group.authorize_ingress(IpProtocol='tcp', FromPort=80, ToPort=80, CidrIp='0.0.0.0/0')  # HTTP access
    else:
        security_group = resource_client.SecurityGroup(response['SecurityGroups'][0]['GroupId'])

        return security_group


# Define a function to check if an EC2 instance with a given name exists
def instance_exists(name, client):
    # Describe instances with a filter based on the given name
    instances = client.describe_instances(Filters=[
        {'Name': 'tag:Name', 'Values': [name]}
    ])['Reservations']
    # Return True and the instances if at least one instance matches the name, otherwise False and instances
    return len(instances) > 0, instances


# AMI_IMAGE_ID = 'ami-02f3f602d23f1659d'  # Amazon Linux 2023 AMI
# DEFAULT_SECURITY_GROUP = "sg-088883dca8b60ae8a"


def create_ec2_instance(name, **kwargs):
    client = kwargs.get("client")
    resource_client = kwargs.get("resource_client")
    security_group_name = kwargs.get("security_group_name")
    options = kwargs.get("options") or {}

    security_group = create_security_group(security_group_name, client, resource_client)

    # Check if an EC2 instance with the given name already exists
    it_exists, _instances = instance_exists(name, client)

    # If the instance exists, print a message and return its information
    if it_exists:
        print(f"Ec2 instance with name '{name}' already exists :)")
        return _instances[0].get("Instances", [])[0]

    # Retrieve the default VPC's ID
    vpc_id = client.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])['Vpcs'][0]['VpcId']

    # Retrieve the subnet ID associated with the VPC
    subnet_id = client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets'][0]['SubnetId']

    # Print a message indicating the creation of the new EC2 instance
    print(f"Currently creating EC2 instance '{name}'...")

    # Create the new EC2 instance with the specified parameters
    instances = client.run_instances(
        ImageId=AMI_IMAGE_ID,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[security_group.id],
        SubnetId=subnet_id,
        IamInstanceProfile={'Arn': LAB_ROLE_PROFILE_ARN},
        **options,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': name
                    },
                ]
            },
        ]
    )

    # Retrieve "Instances" from the response, and if it's not available, provide a fallback empty array
    instances = instances.get("Instances", [])

    # If instances array is not empty, return the first instance's information
    if len(instances):
        return instances[0]

    # If no instances were created, return None
    return None


# testing.........
def lets_see_security_groups(client=None):
    client = client or EC2_CLIENT
    response = client.describe_security_groups()

    # print security group IDs
    for group in response['SecurityGroups']:
        print(group['GroupName'], group['GroupId'])
