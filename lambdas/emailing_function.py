import json
import boto3

sns_client = boto3.client('sns')

print('Loading function')

PEDESTRIAN = "PEDESTRIAN"
PEDESTRIAN_KEY_FROM_REKOGNITION = "Pedestrian"
INSERT = "INSERT"
SNS_TOPIC_ARN = f'arn:aws:sns:us-east-1:122802082660:{PEDESTRIAN}'


def make_message(image_name, confidence):
    confidence = round(float(confidence), 2)
    title = f"New Pedestrian Identified With {confidence}% Certainty!"
    body = f"We are {confidence}% sure we found a pedestrian in this image '{image_name}'"

    return title, body


def lambda_handler(event, context):
    records = event["Records"]
    print("---------- ENTIRE EVENT --------")
    print(event)
    print("...............................")
    first = records[0]
    item = {}
    event_name = first.get("eventName", None)
    if event_name == INSERT:
        item = first['dynamodb']['NewImage']
        key = item["imageKey"]["S"]
        labels = item["labels"]["M"]
        keys = labels.keys()
        found_pedestrian = PEDESTRIAN_KEY_FROM_REKOGNITION in keys
        if found_pedestrian:
            # Send the email here
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
        # print("Labels Here", labels)
    else:
        print("NOT AN INSERT EVENT", event_name)
    return
