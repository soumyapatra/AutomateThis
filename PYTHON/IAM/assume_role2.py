import boto3
import logging


s3_client=boto3.client('s3',aws_access_key_id='xxxxxxxxxxxxxxxxxxx',aws_secret_access_key='xxxxxxxxxxxxxxxxxx')

def get_s3_url(bucket,key,expires=86400):
    try:
        response=s3_client.generate_presigned_url('get_object',Params={'Bucket' :bucket,'Key':key},ExpiresIn=expires)
    except Exception as e:
        logging.error(e)
        return None
    return response

print(get_s3_url('bucket-name','key'))
