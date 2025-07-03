from pprint import pprint
import boto3
import string
import random
import time
from botocore.exceptions import ClientError
import sys
import botocore.exceptions
from boto3.dynamodb.conditions import Key

TABLE_NAME = "stack_details"
REGION = "ap-southeast-1"
endpoint = ""
source = string.ascii_letters + string.digits
d_client = boto3.client("dynamodb", region_name=REGION)


def get_table_status(table_name):
    try:
        response = d_client.describe_table(
            TableName=table_name
        )
        return response["Table"]["TableStatus"]
    except ClientError as e:
        print("exception raised", e.response)
        return e.response["Error"]["Code"]


def create_table(table_name, primary_key):
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    response = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': primary_key,
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': primary_key,
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }
    )

    print("Table status:", response.table_status)
    return response


def create_user():
    user = {
        'id': 1,
        'first_name': 'Jon',
        'last_name': 'Doe',
        'email': 'jdoe@test.com'
    }

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('Users')

    table.put_item(Item=user)


def put_stack_details(stack_id, s3_location, created_by, active, table_nam, region, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name=region)

    table = dynamodb.Table(table_nam)
    response = table.put_item(
        Item={
            'stack_id': stack_id,
            's3_location': s3_location,
            'info': {
                'created_by': created_by,
                'active': active
            }
        }
    )
    return response


if __name__ == '__main__':
    # create_table(TABLE_NAME, "stack_id")
    print(get_table_status(TABLE_NAME))
    if get_table_status(TABLE_NAME) == "ResourceNotFoundException":
        create_table(TABLE_NAME, "stack_id")
        time.sleep(5)

    while get_table_status(TABLE_NAME) != "ACTIVE":
        print(f"Waiting for the table: {TABLE_NAME} to be created")


    print("Put succeeded:")
    pprint(response)

if sys.argv[1] == "add":
    stack_id = ''.join((random.choice(source) for i in range(8)))
    print(stack_id)
    response = put_stack_details(stack_id, f"s3://stage.xxxxxxxx.sonartest/stack_state/{stack_id}", "soumya", "true",
                                 TABLE_NAME, REGION)
