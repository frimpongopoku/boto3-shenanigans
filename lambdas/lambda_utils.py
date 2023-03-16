from utils import create_client, LAB_ROLE_ARN


def lambda_function_exists(**kwargs):
    client = kwargs.get("client")
    name = kwargs.get("function_name")
    try:
        response = client.get_function(FunctionName=name)
        return True, response['Configuration']['FunctionArn']
    except client.exceptions.ResourceNotFoundException:
        return False, None


def create_lambda_function(**kwargs):
    function_name = kwargs.get("function_name")
    role = kwargs.get("role", LAB_ROLE_ARN)
    code_source = kwargs.get("code_source")
    client = kwargs.get("client", create_client("lambda"))
    handler_name = kwargs.get("handler_name")
    it_exists, arn = lambda_function_exists(client=client, function_name=function_name)
    if it_exists:
        print(f"The function '{function_name}' already exists, so it wont be recreated...")
        return arn

    response = client.create_function(
        FunctionName=function_name,
        Runtime='python3.8',
        Role=role,
        Handler= handler_name or 'lambda_function.lambda_handler',
        Code=code_source
    )
    return response["FunctionArn"]


def event_source_mapping_exists(queue_arn, function_name, client):
    response = client.list_event_source_mappings(FunctionName=function_name)
    arns = [mapping["EventSourceArn"] for mapping in response["EventSourceMappings"]]
    print("Here ar the ARNS", arns)
    return queue_arn in arns


def create_lambda_trigger_from_sqs(queue_arn, function_name, **kwargs):
    client = kwargs.get("client", create_client("lambda"))
    it_exists = event_source_mapping_exists(queue_arn, function_name, client)
    if it_exists:
        print(
            f"The source mapping between function '{function_name}' and queue with arn = '{queue_arn}' already exists :)")
        return True
    client.create_event_source_mapping(
        EventSourceArn=queue_arn,
        FunctionName=function_name,
        BatchSize=10,  # Adjust the batch size as needed
        Enabled=True
    )
    print(
        f"Created source mapping between function '{function_name}' and queue with arn = '{queue_arn}'!")
    return True
