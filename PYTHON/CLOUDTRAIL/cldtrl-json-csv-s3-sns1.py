import boto3
import json
from datetime import datetime
from datetime import timedelta
from datetime import date
import csv
import logging
from botocore.exceptions import ClientError

s3_client=boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))
BUCKET='xxxxxxxxxxxxxxxxxxxxx'
KEY=f'ct_data/ct_event-{date.today()}.csv'
SNS= "aws-arn"
FILE= "/tmp/cl_event.csv"
REGION=["ap-south-1","ap-southeast-1"]
def pub_sns(arn,msg):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn = arn,
        Message = msg,
    )
    return response

def get_s3_url(bucket,key,expires=86400):
    try:
        response=s3_client.generate_presigned_url('get_object',Params={'Bucket' :bucket,'Key':key},ExpiresIn=expires)
    except Exception as e:
        logging.error(e)
        return None
    return response

def upload_s3(bucket,key,file):
    try:
        data=open(file,"rb")
        response=s3_client.put_object(Bucket=bucket,Key=key,Body=data)
    except Exception as e:
        logging.error(e)
    return response

def ct_lookup(region):
    ct_client=boto3.client('cloudtrail', region_name=region)
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
    count=0
    for event in response['Events']:
        with open(FILE,"a") as csvFile:
            cl_event=json.loads(event['CloudTrailEvent'])
            response_element=cl_event.get('responseElements')
            if response_element is None:
                continue
            inst_details=cl_event.get('responseElements',{}).get('instancesSet',{}).get('items')
            parsed_data=event.get('EventId'),cl_event.get('sourceIPAddress'),event.get('Username'),cl_event.get('awsRegion'),inst_details[0]["instanceId"],inst_details[0]["instanceType"],event.get('EventTime')
            csvWriter=csv.writer(csvFile)
            csvWriter.writerow(parsed_data)
            count += 1
    return count


col_head="EventID,EventSourceIP,User,Region,InstanceID,InstanceType,EventTime\n"
col_write=open(FILE,"w")
col_write.write(col_head)
col_write.close()
south_count=ct_lookup(REGION[0])
southeast_count=ct_lookup(REGION[1])
print(upload_s3(BUCKET, KEY, FILE))
s3_url = get_s3_url(BUCKET, KEY)
msg = f'Total Instance Launched:  \nSOUTH - {south_count} \nSOUTHEAST - {southeast_count}\n\n\nReport has been Uploaded to: {BUCKET}/{KEY}\n\n\nFollowing is the temporary link to access CSV file: {s3_url}'
pub_sns(SNS, msg)
