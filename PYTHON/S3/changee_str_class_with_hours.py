import boto3
import sys
import time

s3 = boto3.client('s3', region_name="ap-south-1")


def restore_obj(bucket, key):
    response = s3.restore_object(
        Bucket=bucket,
        Key=key,
        RestoreRequest={
            'Days': 123,
            'GlacierJobParameters': {
                'Tier': 'Expedited'
            }})
    return response


def get_obj_head(bucket, key):
    response = s3.head_object(
        Bucket=bucket,
        Key=key
    )["ResponseMetadata"]
    return response["HTTPHeaders"]["x-amz-restore"]


def list_keys(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=123)
    response_list = []
    key_list = []
    if "Contents" in response:
        response_list.extend(response["Contents"])
        while "NextContinuationToken" in response:
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=123,
                                          ContinuationToken=response["NextContinuationToken"])
            response_list.extend(response["Contents"])
        for item in response_list:
            if item["Key"][-1:] != "/" and item["StorageClass"] == "GLACIER":
                key_list.append(item["Key"])
        return key_list
    else:
        return False


def change_str_class(bucket, key, str_class):
    copy_source = {
        'Bucket': bucket,
        'Key': key
    }
    response = s3.copy_object(
        CopySource=copy_source,
        Bucket=bucket,
        Key=key,
        StorageClass=str_class
    )
    return response


filename = './obj.csv'

if len(sys.argv) != 3:
    print("Enter arg as script.py bucket list/copy")
    exit()
else:
    BUC = sys.argv[1]
    action = sys.argv[2]
    if action == "list":
        for i in range(0, 24):
            s3_key = f"structured/E2DQRMZPWI521U/2020/11/20/{i:02}/"
            keys = list_keys(BUC, s3_key)
            for key in keys:
                print(key)
    elif action == "copy":
        for i in range(0, 24):
            s3_key = f"structured/E2DQRMZPWI521U/2020/11/20/{i:02}/"
            keys = list_keys(BUC, s3_key)
            for key in keys:
                restore_obj(BUC, key)
                status = get_obj_head(BUC, key)
                while status == "ongoing-request=\"true\"":
                    print("Waiting for restore to complete")
                    status = get_obj_head(BUC, key)
                    time.sleep(5)
                print(status)
                print(key)
                change_str_class(BUC, key, "STANDARD")
