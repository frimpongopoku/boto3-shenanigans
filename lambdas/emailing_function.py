import json
import boto3

sns_client = boto3.client('sns')

print('Loading function')

PEDESTRIAN = "PEDESTRIAN"
PEDESTRIAN_KEY_FROM_REKOGNITION = "Pedestrian"
INSERT = "INSERT"
SNS_TOPIC_ARN = f'arn:aws:sns:us-east-1:122802082660:{PEDESTRIAN}'


# Define a function that creates an email message with the image name and confidence value
def make_message(image_name, confidence):
    # Round the confidence value to two decimal places
    confidence = round(float(confidence), 2)
    # Use the image name and confidence value to create the email subject and body
    title = f"New Pedestrian Identified With {confidence}% Certainty!"
    body = f"We are {confidence}% sure we found a pedestrian in this image '{image_name}'"

    # Return the title and body as a tuple
    return title, body


# Define the AWS Lambda handler function
def lambda_handler(event, context):
    # Extract the S3 event records from the event object
    records = event["Records"]
    print("---------- ENTIRE EVENT --------")
    print(event)
    print("...............................")

    # Get the first record in the event (assuming there is only one)
    first = records[0]
    item = {}
    # Extract the name of the event ("INSERT", "MODIFY", or "REMOVE")
    event_name = first.get("eventName", None)
    # If the event is an "INSERT" event, extract the image and its labels from the DynamoDB item
    if event_name == INSERT:
        item = first['dynamodb']['NewImage']
        key = item["imageKey"]["S"]
        labels = item["labels"]["M"]
        keys = labels.keys()
        # Check whether the "Pedestrian" label is present in the labels dictionary
        found_pedestrian = PEDESTRIAN_KEY_FROM_REKOGNITION in keys
        if found_pedestrian:
            # If the "Pedestrian" label is present, send an email with the image name and confidence value
            confidence = labels[PEDESTRIAN_KEY_FROM_REKOGNITION]["N"]
            [subject, body] = make_message(key, confidence)
            response = sns_client.publish(TopicArn=SNS_TOPIC_ARN, Message=body, Subject=subject)
            print("Email Response ------>", response)
            print("-------- FOUND----------")
            print("FOUND PEDESTRIAN", found_pedestrian, labels[PEDESTRIAN_KEY_FROM_REKOGNITION])
        else:
            print("We could not find a pedestrian in this image!")
        print("--------- RECORDS HERE -------------")
        print("Key Here", key)
    else:
        print("NOT AN INSERT EVENT", event_name)
    return
