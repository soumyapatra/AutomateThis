import boto3

sts=boto3.client('sts')
print("Default role:",sts.get_caller_identity())

role_2_assume="arn:aws:REDACTED"
role_sess_name="cloudtrail_lambda_session"

response=sts.assume_role(RoleArn=role_2_assume,RoleSessionName=role_sess_name)
creds=response['Credentials']
print(creds)
sts_assumes_role=boto3.client('sts',aws_access_key_id=creds['AccessKeyId'],aws_secret_access_key=creds['SecretAccessKey'],aws_session_token=creds['SessionToken'])
print("Assumed Role Now:",sts_assumes_role.get_caller_identity()['Arn'])
