import time

from utils import STUDENT_ID, create_session, create_client

QUEUE_NAME = f"pongos_sqs_queue_{STUDENT_ID}"


def queue_exists(**kwargs):
    name = kwargs.get("name", None)
    if not name:
        print("Please provide a name for the queue")
        return False, None
    client = kwargs.get("client", create_client("sqs"))
    try:
        response = client.get_queue_url(QueueName=name)
        return True, response
    except client.exceptions.QueueDoesNotExist:
        return False, None


def create_queue(**kwargs):
    name = kwargs.get("name", None)
    client = kwargs.get("client", create_client("sqs"))
    it_exists, sqs = queue_exists(name=name, client=client)
    if it_exists:
        print("Queue already exists, here you go :)")
        return sqs
    response = client.create_queue(QueueName=name)
    queue_url = response['QueueUrl']
    print(f"Queue {name} created with URL: {queue_url}")
    return response
