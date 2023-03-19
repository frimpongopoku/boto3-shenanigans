import time

from utils import create_client, create_stack, STUDENT_ID

TABLE_NAME = "pongosdynamotables2023351"  # Change this value too in dynamo entry lambda if its ever changed


def retrieve_all_table_items(table_name, client):
    response = client.scan(TableName=table_name)
    items = response['Items']

    # Keep  reading until the end even if paginated
    while 'LastEvaluatedKey' in response:
        response = client.scan(TableName=table_name, ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    return items


def get_table_key_schema(table_name, client):
    response = client.describe_table(TableName=table_name)
    key_schema = {key['AttributeName']: key['KeyType'] for key in response['Table']['KeySchema']}
    return key_schema


def empty_database_table(table_name, client):
    exists, _ = table_exists(table_name, client)
    if not exists:
        return True
    items = retrieve_all_table_items(table_name, client)
    schema = get_table_key_schema(table_name, client)
    for item in items:
        key = {k: v for k, v in item.items() if k in schema}
        client.delete_item(TableName=table_name, Key=key)

    return True


def table_exists(name, client):
    try:
        client.describe_table(TableName=name)
        return True, name
    except client.exceptions.ResourceNotFoundException:
        return False, name


def create_table_from_template(table_template, table_name, **kwargs):
    client = kwargs.get("client", create_client("dynamodb"))
    formation_client = kwargs.get("formation_client")

    it_exists, table_name = table_exists(table_name, client)
    if it_exists:
        print(f"[+]The table '{table_name}' you are trying to create already exists :)")
        return table_name

    stack_name = f"pongos-new-dyno-stack-{str(int(time.time()))}-{STUDENT_ID}"
    stack_id = create_stack(stack_name=stack_name, formation_client=formation_client, template=table_template)
    if stack_id:
        return table_name

    return None


def stream_is_enabled(table_name, client):
    response = client.describe_table(TableName=table_name)
    try:
        stream_specification = response['Table']['StreamSpecification']
        if stream_specification['StreamEnabled']:
            return True, response
    except KeyError:
        # if stream is not enabled yet, StreamSpecification will not be available, hence KeError
        return False, response

    return False, None


def enable_streaming_on_dyno_table(table_name, **kwargs):
    client = kwargs.get("client", create_client("dynamodb"))
    exist, table_name = table_exists(table_name, client)
    if not exist:
        print(f"[+]The table you are looking for does not exist  yet, you cant enable streaming...")
        return None

    stream_enabled, response = stream_is_enabled(table_name, client)
    if stream_enabled:
        print(f"[+]Stream is already enabled for this table'{table_name}'...")
        return response["Table"]["LatestStreamArn"]
    try:
        response = client.update_table(
            TableName=table_name,
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': 'NEW_IMAGE'
            }
        )
        return response['TableDescription']['LatestStreamArn']
    except Exception as e:
        print("[-]Error while enabling streaming: ", str(e))
        return None
