import boto3
import time

s3_client = boto3.client("s3")
BUCKET = "xxxxxxxx-logs"
PREFIX_LIST = ["elb-logs/payment-alb-logs/AWSLogs/901680736066/elasticloadbalancing/ap-south-1/2020/11/09/", "elb-logs/payment-alb-logs/AWSLogs/901680736066/elasticloadbalancing/ap-south-1/2020/11/10/", "elb-logs/payment-alb-logs/AWSLogs/901680736066/elasticloadbalancing/ap-south-1/2020/11/11/"]


def list_keys(bucket, prefix, str_class):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=123)
    response_list = []
    key_list = []
    if "Contents" in response:
        response_list.extend(response["Contents"])
        while "NextContinuationToken" in response:
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=123,
                                                 ContinuationToken=response["NextContinuationToken"])
            response_list.extend(response["Contents"])
        for item in response_list:
            if item["Key"][-1:] != "/" and item["StorageClass"] == str_class:
                key_list.append(item["Key"])
        return key_list
    else:
        return False


def restore_obj(bucket, key):
    response = s3_client.restore_object(
        Bucket=bucket,
        Key=key,
        RestoreRequest={
            'Days': 123,
            'GlacierJobParameters': {
                'Tier': 'Expedited'
            }})
    return response


def get_obj_head(bucket, key):
    response = s3_client.head_object(
        Bucket=bucket,
        Key=key
    )["ResponseMetadata"]
    return response["HTTPHeaders"]["x-amz-restore"]


def change_str_class(bucket, key, str_class):
    copy_source = {
        'Bucket': bucket,
        'Key': key
    }
    response = s3_client.copy_object(
        CopySource=copy_source,
        Bucket=bucket,
        Key=key,
        StorageClass=str_class
    )
    return response


for prefix in PREFIX_LIST:
    keys = list_keys(BUCKET, prefix, "GLACIER")
    print(keys)
    for key in keys:
        restore_obj(BUCKET, key)
        status = get_obj_head(BUCKET, key)
        while status == "ongoing-request=\"true\"":
            print("Waiting for restore to complete")
            status = get_obj_head(BUCKET, key)
            time.sleep(5)
        print(status)
        print(change_str_class(BUCKET, key, "STANDARD"))
