# Lambda Function to handle processing image information with Rekognition and saving to dynamo db
import json


def lambda_handler(event, context):
    message = 'Hello there, I am meant to be for DYNAMO ENTRY!'
    return {
        'statusCode': 200,
        'body': json.dumps({'message': message})
    }
