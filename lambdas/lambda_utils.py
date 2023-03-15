from utils import create_client, LAB_ROLE_ARN


def create_lambda_function(**kwargs):
    function_name = kwargs.get("function_name")
    role = kwargs.get("role", LAB_ROLE_ARN)
    code_source = kwargs.get("code_source")

    client = kwargs.get("client", create_client("lambda"))
    response = client.create_function(
        FunctionName=function_name,
        Runtime='python3.8',
        Role=role,
        Handler='lambda_function.lambda_handler',
        Code=code_source
    )
    return response








    # Code = {
    #            'S3Bucket': 'my-lambda-code-bucket',
    #            'S3Key': 'lambda_function.zip'
    #        },
