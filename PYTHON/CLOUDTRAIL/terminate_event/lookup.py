import boto3
import logging
import json
import csv
from datetime import date
from datetime import datetime
from datetime import timedelta
def ct_lookup():
    ct_client=boto3.client('cloudtrail')
    response=ct_client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventName',
                'AttributeValue': 'TerminateInstances'
            },
        ],
        StartTime=datetime.now()-timedelta(days=1),
        EndTime=datetime.now(),
    )
    for event in response["Events"]:
        cl_event=json.loads(event["CloudTrailEvent"])
        print(cl_event)


ct_lookup()
