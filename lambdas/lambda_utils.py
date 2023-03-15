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
    it_exists, arn = lambda_function_exists(client=client, function_name=function_name)
    if it_exists:
        print(f"The function '{function_name}' already exists, so it wont be recreated...")
        return arn

    response = client.create_function(
        FunctionName=function_name,
        Runtime='python3.8',
        Role=role,
        Handler='lambda_function.lambda_handler',
        Code=code_source
    )
    return response["FunctionArn"]
