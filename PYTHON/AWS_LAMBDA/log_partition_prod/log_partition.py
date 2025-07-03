import boto3
import json


def lambda_handler(event, context):
    print(json.dumps(event))
    s3 = boto3.client('s3')
    print("Im trying to work with your logs")
    athena_info = dict()
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        filename = key.split('/')[1]
        distro = filename.split('.')[0].split('/')[0]
        dateAndHour = filename.split('.')[1].split('/')[0]
        year, month, day, hour = dateAndHour.split('-')
        dest = 'structured/{}/{}/{}/{}/{}/{}'.format(
            distro, year, month, day, hour, filename
        )
        athena_info['id'] = distro
        athena_info['year'] = year
        athena_info['month'] = month
        athena_info['day'] = day
        athena_info['hour'] = hour
        print("- src: s3://%s/%s" % (bucket, key))
        print("- dst: s3://%s/%s" % (bucket, dest))
        s3.copy_object(Bucket=bucket, Key=dest, CopySource=bucket + '/' + key)
        print(json.dumps(athena_info))
       # s3.delete_object(Bucket=bucket, Key=key)
    print("Invoking Athena Alter lambda ")
    lamb = boto3.client('lambda')
    req_forward = lamb.invoke(FunctionName='athena_alter_cf_table', InvocationType='Event', Payload=json.dumps(athena_info))
    print(req_forward)