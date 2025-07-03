import boto3
import json
from datetime import datetime
from datetime import timedelta


cldtr=boto3.client('cloudtrail')
response=cldtr.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventId',
                'AttributeValue': 'db2b7543-2f02-44b0-af07-00d70c11f636'
            },
        ],
        StartTime=datetime.now()-timedelta(days=1),
        EndTime=datetime.now(),
    )
y=json.loads(response['Events'][0]['CloudTrailEvent'])
for request in y["requestParameters"]:
    z=json.loads(request)
    print(z)
 #   print(y["userIdentity"]["userName"],y["eventTime"],y["awsRegion"],y["sourceIPAddress"],y["responseElements"]["instancesSet"]["items"]["instanceId"])


