import time

from utils import create_client, create_stack, STUDENT_ID

TABLE_NAME = "pongosdynamotables2023351"  # Change this value too in dynamo entry lambda if its ever changed


# Define the function to retrieve all items from a DynamoDB table
def retrieve_all_table_items(table_name, client):
    # Perform an initial scan operation on the specified table and store the response
    response = client.scan(TableName=table_name)
    # Extract the list of items from the response
    items = response['Items']

    # Continue reading items from the table if the response is paginated
    # (i.e., there's a 'LastEvaluatedKey' in the response, indicating there are more items to retrieve)
    while 'LastEvaluatedKey' in response:
        # Perform another scan operation on the table, starting from the last evaluated key
        response = client.scan(TableName=table_name, ExclusiveStartKey=response['LastEvaluatedKey'])
        # Extend the items list with the new items retrieved in the current response
        items.extend(response['Items'])

    # Return the complete list of items retrieved from the table
    return items


# Define the function to get the key schema of a DynamoDB table
def get_table_key_schema(table_name, client):
    # Call the describe_table method on the client to get table details
    response = client.describe_table(TableName=table_name)
    # Extract and format the key schema from the response
    key_schema = {key['AttributeName']: key['KeyType'] for key in response['Table']['KeySchema']}
    # Return the key schema as a dictionary
    return key_schema


# Define a function to delete all items in a DynamoDB table
def empty_database_table(table_name, client):
    # Check if the table exists and get its status
    exists, _ = table_exists(table_name, client)
    # If the table does not exist, return True
    if not exists:
        return True
    # Retrieve all items from the table
    items = retrieve_all_table_items(table_name, client)
    # Get the key schema of the table
    schema = get_table_key_schema(table_name, client)
    # Iterate through each item
    for item in items:
        # Create a key dictionary containing only the key attributes of the item
        key = {k: v for k, v in item.items() if k in schema}
        # Delete the item using its key
        client.delete_item(TableName=table_name, Key=key)

    # Return True after all items are deleted
    return True


# Define a function to check if a DynamoDB table exists
def table_exists(name, client):
    try:
        # Attempt to describe the table
        client.describe_table(TableName=name)
        # If successful, return True and the table name
        return True, name
    except client.exceptions.ResourceNotFoundException:
        # If the table is not found, return False and the table name
        return False, name


# Define a function to create a DynamoDB table from a CloudFormation template
def create_table_from_template(table_template, table_name, **kwargs):
    # Get the DynamoDB client or create a new one
    client = kwargs.get("client", create_client("dynamodb"))
    # Get the CloudFormation client from kwargs
    formation_client = kwargs.get("formation_client")

    # Check if the table exists
    it_exists, table_name = table_exists(table_name, client)
    # If the table exists, print a message and return the table name
    if it_exists:
        print(f"[+]The table '{table_name}' you are trying to create already exists :)")
        return table_name

    # Generate a unique stack name
    stack_name = f"pongos-new-dyno-stack-{str(int(time.time()))}-{STUDENT_ID}"
    # Create the CloudFormation stack and get its ID
    stack_id = create_stack(stack_name=stack_name, formation_client=formation_client, template=table_template)
    # If the stack was created successfully, return the table name
    if stack_id:
        return table_name

    # If the stack creation failed, return None
    return None


# Define a function to check if a DynamoDB table's stream is enabled
def stream_is_enabled(table_name, client):
    # Describe the table and get the response
    response = client.describe_table(TableName=table_name)
    try:
        # Extract the stream specification from the response
        stream_specification = response['Table']['StreamSpecification']
        # If the stream is enabled, return True and the response
        if stream_specification['StreamEnabled']:
            return True, response
    except KeyError:
        # If StreamSpecification is not present, return False and the response
        return False, response

    # Return False and None if the function hasn't returned earlier
    return False, None


# Define a function to enable streaming on a DynamoDB table
def enable_streaming_on_dyno_table(table_name, **kwargs):
    # Get the DynamoDB client or create a new one
    client = kwargs.get("client", create_client("dynamodb"))
    # Check if the table exists
    exist, table_name = table_exists(table_name, client)
    # If the table does not exist, print a message and return None
    if not exist:
        print(f"[+]The table you are looking for does not exist  yet, you cant enable streaming...")
        return None

    # Check if the stream is enabled
    stream_enabled, response = stream_is_enabled(table_name, client)
    # If the stream is enabled, print a message and return the stream ARN
    if stream_enabled:
        print(f"[+]Stream is already enabled for this table'{table_name}'...")
        return response["Table"]["LatestStreamArn"]
    try:
        # Update the table to enable streaming
        response = client.update_table(
            TableName=table_name,
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': 'NEW_IMAGE'
            }
        )
        # Return the latest stream ARN
        return response['TableDescription']['LatestStreamArn']
    except Exception as e:
        # If an error occurs, print a message and return None
        print("[-]Error while enabling streaming: ", str(e))
        return None
