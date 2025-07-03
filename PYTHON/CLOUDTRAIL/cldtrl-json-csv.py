import boto3
import json
from datetime import datetime
from datetime import timedelta
import csv

def get_log():
    ct_client=boto3.client('cloudtrail')
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
    col_head="EventID,EventSourceIP,User,Region,InstanceID,InstanceType,EventTime\n"
    col_write=open("./cl_event.csv","w")
    col_write.write(col_head)
    col_write.close()
    #print(response["Events"])
    for event in response['Events']:
        with open("./cl_event.csv","a") as csvFile:
            cl_event=json.loads(event['CloudTrailEvent'])
            response_element=cl_event.get('responseElements')
            if response_element is None:
                continue
            inst_details=cl_event.get('responseElements',{}).get('instancesSet',{}).get('items')
            parsed_data=event.get('EventId'),cl_event.get('sourceIPAddress'),cl_event.get('awsRegion'),inst_details[0]["instanceId"],inst_details[0]["instanceType"],event.get('EventTime')
            csvWriter=csv.writer(csvFile)
            csvWriter.writerow(parsed_data)
            
        #print(cl_event.get('eventID'),cl_event.get('awsRegion'),cl_event.get('userIdentity',{}).get('userName'),cl_event.get('sourceIPAddress'),inst_details[0]["instanceId"],inst_details[0]["instanceType"])
get_log()

