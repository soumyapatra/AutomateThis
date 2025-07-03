import json
import boto3

REGION = 'ap-southeast-1'

dynamodb_client = boto3.resource('dynamodb', region_name=REGION)

LAUNCH_TABLE_NAME = "launch-instance-details"
TERMINATE_TABLE_NAME = 'terminate-instance-details'

# Create table if not exist
table_names = [table.name for table in dynamodb_client.tables.all()]
if LAUNCH_TABLE_NAME not in table_names:
    table = dynamodb_client.create_table(TableName=LAUNCH_TABLE_NAME,
                                         KeySchema=[{'AttributeName': 'instance-id', 'KeyType': 'HASH'}],
                                         AttributeDefinitions=[{'AttributeName': 'instance-id', 'AttributeType': 'S'}],
                                         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1})
    table.meta.client.get_waiter('table_exists').wait(TableName=LAUNCH_TABLE_NAME)
if TERMINATE_TABLE_NAME not in table_names:
    table = dynamodb_client.create_table(TableName=TERMINATE_TABLE_NAME,
                                         KeySchema=[{'AttributeName': 'instance-id', 'KeyType': 'HASH'}],
                                         AttributeDefinitions=[{'AttributeName': 'instance-id', 'AttributeType': 'S'}],
                                         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1})
    table.meta.client.get_waiter('table_exists').wait(TableName=TERMINATE_TABLE_NAME)


def update_dynamodb(inst_id, event, time, ip, type=None):
    if event == "RunInstances":
        table = dynamodb_client.Table(LAUNCH_TABLE_NAME)
        table.put_item(
            Item={
                'instance-id': inst_id,
                'type': type,
                'event': event,
                'time': time,
                'source-ip': ip,
            }
        )
    elif event == "TerminateInstances":
        table = dynamodb_client.Table(TERMINATE_TABLE_NAME)
        table.put_item(
            Item={
                'instance-id': inst_id,
                'event': event,
                'time': time,
                'source-ip': ip,
            }
        )


def get_inst_type(inst_id):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_attribute(Attribute='instanceType', InstanceId=inst_id)
    return response


def lambda_handler(event, context):
    print(json.dumps(event))
    event_details = event['detail']
    instance_details = event_details['responseElements']['instancesSet']['items'][0]
    event_name = event_details['eventName']
    event_time = event_details['eventTime']
    src_ip = event_details['sourceIPAddress']
    if event_name == "RunInstances":
        print("Instance Ran")
        instance_id = instance_details['instanceId']
        instance_type = instance_details['instanceType']
        print(instance_id, event_name, event_time, src_ip, instance_type)
        update_dynamodb(instance_id, event_name, event_time, src_ip, instance_type)
    elif event_name == "TerminateInstances":
        print("Instance Terminated")
        instance_id = instance_details['instanceId']
        # instance_type = get_inst_type(instance_id)
        print(instance_id, event_name, event_time, src_ip)
        update_dynamodb(instance_id, event_name, event_time, src_ip)
