import boto3
import json
from datetime import datetime
from datetime import timedelta
from datetime import date
import csv
import logging
import os

ct_client=boto3.client('cloudtrail', region_name="ap-southeast-1")
response=ct_client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventName',
                'AttributeValue': 'RunInstances'
            },
        ],
        StartTime=datetime.now()-timedelta(days=1),
        EndTime=datetime.now(),
    )
for event in response['Events']:
    cl_event = json.loads(event['CloudTrailEvent'])
    response_element = cl_event.get('responseElements')
    if response_element is None:
        continue
    inst_details = cl_event.get('responseElements', {}).get('instancesSet', {}).get('items')
    parsed_data = event.get('EventId'), cl_event.get('sourceIPAddress'), event.get('Username'), cl_event.get('awsRegion'), inst_details[0]["instanceId"], inst_details[0]["instanceType"], event.get('EventTime')

print(cl_event)
