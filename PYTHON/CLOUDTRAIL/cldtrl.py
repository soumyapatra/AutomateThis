import boto3
from datetime import datetime
from datetime import timedelta

def get_log():
    cldtr=boto3.client('cloudtrail')
    response=cldtr.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventId',
                'AttributeValue': 'dc807841-76cd-4138-b88a-81970439731c'
            },
        ],
        StartTime=datetime.now()-timedelta(days=1),
        EndTime=datetime.now(),
    )
    print(response["Events"])    
get_log()

