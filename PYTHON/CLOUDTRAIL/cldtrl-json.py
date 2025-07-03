import boto3
import json
from datetime import datetime
from datetime import timedelta

def get_log():
    cldtr=boto3.client('cloudtrail')
    response=cldtr.lookup_events(
        LookupAttributes=[
            {
                #'AttributeKey': 'EventId',
                #'AttributeValue': 'db2b7543-2f02-44b0-af07-00d70c11f636'
                'AttributeKey': 'EventName',
                'AttributeValue': 'RunInstances'
            },
        ],
        StartTime=datetime.now()-timedelta(days=1),
        EndTime=datetime.now(),
    )
    #print(response["Events"])
    cnt=0
    for event in response['Events']:
        evnts=json.loads(event['CloudTrailEvent'])
        response_element=evnts.get('responseElements')
        if response_element is None:
            continue	
        inst_details=evnts.get('responseElements',{}).get('instancesSet',{}).get('items')
        print(event.get('EventId'),evnts.get('sourceIPAddress'),evnts.get('awsRegion'),inst_details[0]["instanceId"],inst_details[0]["instanceType"],event.get('EventTime'))
        cnt += 1
    print(cnt)
        #print(evnts.get('eventID'),evnts.get('awsRegion'),evnts.get('userIdentity',{}).get('userName'),evnts.get('sourceIPAddress'),inst_details[0]["instanceId"],inst_details[0]["instanceType"])
get_log()
