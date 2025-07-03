import boto3


def chk_obj(bucket,s3_key):
    s3=boto3.client('s3')
    response=s3.list_objects(Bucket=bucket,Prefix=s3_key)
    if "Contents" not in response:
        return False
    else:
        return True

if chk_obj('xxxxxxxx-alblogs','alb-logs/AWSLogs/272110293415/elasticloadbalancing/ap-southeast-1/2019/11/06/'):
    print("TRUE")
