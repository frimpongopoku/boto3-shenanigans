from utils import create_client

TOPIC_NAME = "PEDESTRIAN"  # NB: Change this in emailing lambda too if ever changed here

EMAIL_LIST = ["f.agyemang@alustudent.com", "cpd.aws@example.com"]


# Define a function to check if an SNS topic exists
def topic_exists(topic_name, client):
    # List all SNS topics
    topics = client.list_topics()
    # Check if the topic_name is in any of the listed topics
    for topic in topics['Topics']:
        if topic_name in topic['TopicArn']:
            arn = topic['TopicArn']
            return True, arn
    return False, None


# Define a function to create an SNS topic
def create_sns_topic(topic_name, **kwargs):
    # Get the SNS client from kwargs or create one
    client = kwargs.get("client") or create_client("sns")
    # Check if the topic exists
    it_exists, arn = topic_exists(topic_name, client)
    # If the topic exists, print a message and return its ARN
    if it_exists:
        print(f"[+]A topic with the name '{arn}' exists, here you go...")
        return arn
    # Create the SNS topic
    response = client.create_topic(Name=topic_name)
    # Return the ARN of the created topic
    return response['TopicArn']


# Define a function to subscribe emails to an SNS topic
def subscribe_emails_to_topic(email_list, topic_arn, **kwargs):
    # Get the SNS client from kwargs or create one
    client = kwargs.get("client") or create_client("sns")
    # Loop through the email list
    for email in email_list:
        try:
            # Subscribe each email to the topic
            client.subscribe(
                TopicArn=topic_arn,
                Protocol='email',
                Endpoint=email
            )
        except Exception as e:
            # Print a failure message if an exception occurs
            print("[-]Failed Subscription: ", str(e))
            return False
    # Return True if all subscriptions are successful
    return True
