import boto3
import logging

sts=boto3.client('sts')
print("Default role:",sts.get_caller_identity())

role_2_assume="arn:aws:REDACTED"
role_sess_name="cloudtrail_lambda_session"

response=sts.assume_role(RoleArn=role_2_assume,RoleSessionName=role_sess_name,DurationSeconds=39600)
print(response)
creds=response['Credentials']

sts_assumes_role=boto3.client('sts',aws_access_key_id=creds['AccessKeyId'],aws_secret_access_key=creds['SecretAccessKey'],aws_session_token=creds['SessionToken'])
print("Assumed Role Now:",sts_assumes_role.get_caller_identity()['Arn'])

s3_client=boto3.client('s3',aws_access_key_id=creds['AccessKeyId'],aws_secret_access_key=creds['SecretAccessKey'],aws_session_token=creds['SessionToken'])

def get_s3_url(bucket,key,expires=86400):
    try:
        response=s3_client.generate_presigned_url('get_object',Params={'Bucket' :bucket,'Key':key},ExpiresIn=expires)
    except Exception as e:
        logging.error(e)
        return None
    return response

print(get_s3_url('stage.xxxxxxxx.sonartest','ct_data/ct_event-2019-05-13.csv'))
