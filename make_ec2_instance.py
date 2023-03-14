import boto3
from utils import STUDENT_ID, create_session

# The name of the instance to be created
INSTANCE_NAME = "pongos_assignment_ec2_" + STUDENT_ID

SESSION = create_session()
EC2_CLIENT = SESSION.client('ec2')


def instance_exists(name):
    instances = EC2_CLIENT.describe_instances(Filters=[
        {'Name': 'tag:Name', 'Values': [name]}
    ])['Reservations']
    return len(instances) > 0, instances


AMI_IMAGE_ID = 'ami-0a887e401f7654935'  # Amazon Linux 2 AMI (HVM)

DEFAULT_SECURITY_GROUP = "sg-088883dca8b60ae8a"


def create_ec2_instance(name):
    it_exists, _instances = instance_exists(name)
    if it_exists:
        print(f"Ec2 instance with name '{name}' already exists :)")
        return _instances[0].get("Instances", [])[0]

    vpc_id = EC2_CLIENT.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])['Vpcs'][0][
        'VpcId']
    subnet_id = EC2_CLIENT.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets'][0][
        'SubnetId']
    # Create a new instance if it doesn't exist
    print(f"Currently creating EC2 instance '{name}'...")
    instances = EC2_CLIENT.run_instances(
        ImageId=AMI_IMAGE_ID,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[DEFAULT_SECURITY_GROUP],  # change
        SubnetId=subnet_id,
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
    # Retrieve "Instances" and if its not available, provide a fallback empty array
    instances = instances.get("Instances", [])
    if len(instances):
        return instances[0]
    return None


def lets_see_security_groups():
    response = EC2_CLIENT.describe_security_groups()

    # print security group IDs
    for group in response['SecurityGroups']:
        print(group['GroupName'], group['GroupId'])
