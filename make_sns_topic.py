from utils import create_client

TOPIC_NAME = "PEDESTRIAN" # NB: Change this in emailing lambda too if ever changed here

EMAIL_LIST = ["f.agyemang@alustudent.com"]  # TODO: Before submission, remember to add the email "cpd.aws@example.com"


def topic_exists(topic_name, client):
    topics = client.list_topics()
    for topic in topics['Topics']:
        if topic_name in topic['TopicArn']:
            arn = topic['TopicArn']
            return True, arn
    return False, None


def create_sns_topic(topic_name, **kwargs):
    client = kwargs.get("client", create_client("sns"))
    it_exists, arn = topic_exists(topic_name, client)
    if it_exists:
        print(f"[+]A topic with the name '{arn}' exists, here you go...")
        return arn
    response = client.create_topic(Name=topic_name)
    return response['TopicArn']


def subscribe_emails_to_topic(email_list, topic_arn, **kwargs):
    client = kwargs.get("client", create_client("sns"))
    for email in email_list:
        try:
            client.subscribe(
                TopicArn=topic_arn,
                Protocol='email',
                Endpoint=email
            )
        except Exception as e:
            print("[-]Failed Subscription: ", str(e))
            return False
    return True
