import json
import boto3
from datetime import datetime
from datetime import timedelta

REGION = 'ap-southeast-1'
DAYS = 1

CRAWLERS = ['inst_launch_crawler', 'inst_terminate_crawler']

dynamodb_client = boto3.resource('dynamodb', region_name=REGION)

LAUNCH_TABLE_NAME = "launch-instance-details-test"
TERMINATE_TABLE_NAME = 'terminate-instance-details-test'

# Create table if not exist
table_names = [table.name for table in dynamodb_client.tables.all()]
if LAUNCH_TABLE_NAME not in table_names:
    table = dynamodb_client.create_table(TableName=LAUNCH_TABLE_NAME,
                                         KeySchema=[{'AttributeName': 'inst_id', 'KeyType': 'HASH'}],
                                         AttributeDefinitions=[{'AttributeName': 'inst_id', 'AttributeType': 'S'}],
                                         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1})
    table.meta.client.get_waiter('table_exists').wait(TableName=LAUNCH_TABLE_NAME)
if TERMINATE_TABLE_NAME not in table_names:
    table = dynamodb_client.create_table(TableName=TERMINATE_TABLE_NAME,
                                         KeySchema=[{'AttributeName': 'inst_id', 'KeyType': 'HASH'}],
                                         AttributeDefinitions=[{'AttributeName': 'inst_id', 'AttributeType': 'S'}],
                                         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1})
    table.meta.client.get_waiter('table_exists').wait(TableName=TERMINATE_TABLE_NAME)


def update_dynamodb(inst_id, event, time, ip, type=None):
    if event == "RunInstances":
        table = dynamodb_client.Table(LAUNCH_TABLE_NAME)
        table.put_item(
            Item={
                'inst_id': inst_id,
                'type': type,
                'event': event,
                'time': time,
                'src_ip': ip,
            }
        )
    elif event == "TerminateInstances":
        table = dynamodb_client.Table(TERMINATE_TABLE_NAME)
        table.put_item(
            Item={
                'inst_id': inst_id,
                'event': event,
                'time': time,
                'src_ip': ip,
            }
        )


def get_ct_log(days, eventname):
    ct_client = boto3.client('cloudtrail')
    events = []
    start_time = datetime.now() - timedelta(days=days)
    end_time = datetime.now()
    response = ct_client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventName',
                'AttributeValue': eventname
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=100
    )
    events.extend(response['Events'])
    while 'NextToken' in response:
        response = ct_client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': eventname
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            MaxResults=100,
            NextToken=response['NextToken']
        )
        events.extend(response['Events'])
    return events


inst_running_events = get_ct_log(DAYS, 'RunInstances')

for event in inst_running_events:
    if "errorCode" in event:
        print("Instance not deployed. Ignoring")
        continue
    event = json.loads(event['CloudTrailEvent'])
    src_ip = event['sourceIPAddress']
    instance_details = event['responseElements']['instancesSet']['items'][0]
    instance_id = instance_details['instanceId']
    instance_type = instance_details['instanceType']
    event_time = event['eventTime']
    print(instance_id, instance_type, src_ip, event_time)
    # update_dynamodb(instance_id, 'RunInstances', event_time, src_ip, instance_type)

inst_terminate_events = get_ct_log(DAYS, 'TerminateInstances')

for event in inst_terminate_events:
    event = json.loads(event['CloudTrailEvent'])
    src_ip = event['sourceIPAddress']
    instance_details = event['responseElements']['instancesSet']['items'][0]
    instance_id = instance_details['instanceId']
    event_time = event['eventTime']
    print(instance_id, src_ip, event_time)
    # update_dynamodb(instance_id, 'TerminateInstances', event_time, src_ip)


def list_crawler(region):
    glue_client = boto3.client('')
