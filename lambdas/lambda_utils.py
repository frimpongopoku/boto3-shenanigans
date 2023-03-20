from utils import create_client, LAB_ROLE_ARN


# Define a function that checks whether an AWS Lambda function exists
def lambda_function_exists(**kwargs):
    # Get the client and function_name parameters from kwargs
    client = kwargs.get("client")
    name = kwargs.get("function_name")

    # Try to get the configuration of the function associated with the provided name
    try:
        response = client.get_function(FunctionName=name)
        # If the function is found, return a tuple indicating that it exists, along with its ARN
        return True, response['Configuration']['FunctionArn']
    # If the function is not found, catch the ResourceNotFoundException exception and return a tuple indicating that it does not exist
    except client.exceptions.ResourceNotFoundException:
        return False, None


# Define a function that creates an AWS Lambda function
def create_lambda_function(**kwargs):
    # Get the function_name, role, code_source, client, and handler_name parameters from kwargs
    function_name = kwargs.get("function_name")
    role = kwargs.get("role", LAB_ROLE_ARN)
    code_source = kwargs.get("code_source")
    client = kwargs.get("client", create_client("lambda"))
    handler_name = kwargs.get("handler_name")

    # Check whether the function already exists
    it_exists, arn = lambda_function_exists(client=client, function_name=function_name)
    # If it exists, print a message and return its ARN
    if it_exists:
        print(f"[+]The function '{function_name}' already exists, so it won't be recreated...")
        return arn

    # If the function does not exist, create it by calling the create_function method of the Lambda client
    response = client.create_function(
        FunctionName=function_name,
        Runtime='python3.8',
        Role=role,
        Handler=handler_name or 'lambda_function.lambda_handler',
        Code=code_source
    )
    # Return the ARN of the created function
    return response["FunctionArn"]


# Define a function that checks whether an event source mapping exists between an SQS queue and a Lambda function
def event_source_mapping_exists(queue_arn, function_name, client):
    # Call the list_event_source_mappings method of the Lambda client, passing in the function name
    response = client.list_event_source_mappings(FunctionName=function_name)
    # Extract the ARNs of the event sources associated with the function from the response
    arns = [mapping["EventSourceArn"] for mapping in response["EventSourceMappings"]]
    # Check whether the provided queue ARN is in the list of event source ARNs
    return queue_arn in arns


# Define a function that creates an event source mapping between an SQS queue and a Lambda function
def create_event_source_mapping(arn, function_name, **kwargs):
    # Get the client and options parameters from kwargs, or create new ones if they are not provided
    client = kwargs.get("client", create_client("lambda"))
    options = kwargs.get("options", {})

    # Check whether an event source mapping already exists between the queue and the function
    it_exists = event_source_mapping_exists(arn, function_name, client)
    # If it exists, print a message and return True
    if it_exists:
        print(
            f"[+]The source mapping between function '{function_name}' and queue with arn = '{arn}' already exists :)")
        return True

    # If it does not exist, create it by calling the create_event_source_mapping method of the Lambda client
    client.create_event_source_mapping(
        EventSourceArn=arn,
        FunctionName=function_name,
        BatchSize=10,  # Adjust the batch size as needed
        Enabled=True,
        **options
    )
    print(
        f"[+]Created source mapping between function '{function_name}' and entity with arn = '{arn}'!")
    return True


def create_lambda_trigger_from_sqs(queue_arn, function_name, **kwargs):
    return create_event_source_mapping(queue_arn, function_name, **kwargs) # TODO: remove this entire function later, no need for this
