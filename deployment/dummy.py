import boto3

# from utils import create_session

# SESSION = create_session() # change this before deployment
SESSION = boto3.Session(region_name="us-east-1")
EC2 = SESSION.client("ec2")


def run():
    response = EC2.describe_security_groups()
    print("--------------- WE ARE ABOUT TO DO YOUR LISTING -------------")
    # print security group IDs
    for group in response['SecurityGroups']:
        print(group['GroupName'], group['GroupId'])


def start():
    inp = input("Choose An Option \nA. List Security Groups \nB. Quit Application\n>")
    val = inp.lower()
    if val == "a":
        run()
        start()
    elif val == "b":
        exit()
    else:
        start()


start()
