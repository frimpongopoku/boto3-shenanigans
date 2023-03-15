import time

from utils import create_client, create_stack, STUDENT_ID

TABLE_NAME = "pongosdynamotables2023351"


def table_exists(**kwargs):
    name = kwargs.get("name")
    client = kwargs.get("client") or create_client("dynamodb")
    try:
        client.describe_table(TableName=name)
        return True, name
    except client.exceptions.ResourceNotFoundException:
        return False, name


def create_table_from_template(**kwargs):
    table_name = kwargs.get("table_name")
    table_template = kwargs.get("template")
    client = kwargs.get("client", create_client("dynamodb"))
    formation_client = kwargs.get("formation_client")

    it_exists, table_name = table_exists(name=table_name, client=client)
    if it_exists:
        print(f"The table '{table_name}' you are trying to create already exists :)")
        return table_name

    stack_name = f"pongos-new-dyno-stack-{str(int(time.time()))}-{STUDENT_ID}"
    stack_id = create_stack(stack_name=stack_name, formation_client=formation_client, template=table_template)
    if stack_id:
        return table_name

    return None
