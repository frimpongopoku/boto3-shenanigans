# Lambda Function to handle processing image information with Rekognition and saving to dynamo db
import json
import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.client('dynamodb')
TABLE_NAME = "pongosdynamotables2023351"

print('Loading function')


# Define a function that retrieves an image from an S3 bucket
def get_image(bucket_name, file_name):
    # Call the get_object method of the S3 client, passing in the bucket name and file name
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    # Return the body of the response (which contains the image data)
    return response['Body'].read()


# Define a function that sorts an array of AWS Rekognition labels according to their confidence values
def sort_according_to_confidence(array):
    # Call the sorted method on the array, passing in a lambda function that extracts the "Confidence" value from each dictionary and sorts them in descending order
    return sorted(array, key=lambda item: item['Confidence'], reverse=True)


# Define a function that sends an image's top labels to a DynamoDB table
def send_to_dyno(image_name, top_labels):
    # Create a dictionary that represents the DynamoDB item to be added to the table
    labels = {}
    for label in top_labels:
        name = label["Name"]
        confidence = label["Confidence"]
        labels[name] = {"N": str(confidence)}

    dyno_item = {
        "imageKey": {"S": image_name},
        "labels": {"M": labels}
    }

    # Add the item to the DynamoDB table by calling the put_item method of the DynamoDB client
    return dynamodb.put_item(
        TableName=TABLE_NAME,
        Item=dyno_item
    )


# Define the AWS Lambda handler function
def lambda_handler(event, context):
    # Extract the bucket name and file name from the S3 event record in the SQS message
    sqs_message = event['Records'][0]['body']
    s3_info = json.loads(sqs_message)['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    file_name = s3_info['object']['key']

    # Retrieve the image from the S3 bucket
    image = get_image(bucket_name, file_name)
    # Detect labels in the image using AWS Rekognition
    response = rekognition.detect_labels(Image={'Bytes': image})
    labels = response['Labels']
    # Sort the labels according to their confidence values, and keep only the top five
    labels = sort_according_to_confidence(labels)[:5]

    print("---------------------Detected labels -----------------------")
    for label in labels:
        string = label["Name"] + " : " + str(round(label["Confidence"], 2)) + "% "
        print(string)

    # Send the image's top labels to the DynamoDB table
    res = send_to_dyno(file_name, labels)

    print("-------------------Response After Dyno ------------------------")
    print(res)
