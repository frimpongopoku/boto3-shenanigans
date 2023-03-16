# Lambda function for processing dynamodb stream and sending email if it identifies a passenger
import json


def lambda_handler(event, context):
    message = 'Hello there, I am meant to be for EMAILING!'
    return {
        'statusCode': 200,
        'body': json.dumps({'message': message})
    }
