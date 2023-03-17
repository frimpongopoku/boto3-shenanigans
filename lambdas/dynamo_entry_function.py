# Lambda Function to handle processing image information with Rekognition and saving to dynamo db
import json
import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.client('dynamodb')
TABLE_NAME = "pongosdynamotables2023351"

print('Loading function')


def get_image(bucket_name, file_name):
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    # Detect labels in the image
    return response['Body'].read()


def sort_according_to_confidence(array):
    return sorted(array, key=lambda item: item['Confidence'], reverse=True)


def send_to_dyno(image_name, top_labels):
    labels = {}
    for label in top_labels:
        name = label["Name"]
        confidence = label["Confidence"]
        labels[name] = {"N": str(confidence)}

    dyno_item = {
        "imageKey": {"S": image_name},
        "labels": {"M": labels}
    }

    return dynamodb.put_item(
        TableName=TABLE_NAME,
        Item=dyno_item
    )


def lambda_handler(event, context):
    sqs_message = event['Records'][0]['body']
    s3_info = json.loads(sqs_message)['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    file_name = s3_info['object']['key']

    image = get_image(bucket_name, file_name)
    response = rekognition.detect_labels(Image={'Bytes': image})
    labels = response['Labels']
    labels = sort_according_to_confidence(labels)  # Get first five

    print("---------------------Detected labels -----------------------")
    for label in labels:
        string = label["Name"] + " : " + str(round(label["Confidence"], 2)) + "% "
        print(string)

    res = send_to_dyno(file_name, labels[:5])

    print("-------------------Response After Dyno ------------------------")
    print(res)
