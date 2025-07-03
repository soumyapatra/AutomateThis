
import boto3

def upload_to_s3(filename, bucket_name, key):
    s3 = boto3.client('s3')
    resp = s3.upload_file(filename, bucket_name, key)
    return resp
s3_key = f'stage_ami_deletion_backup/snapshot_details'
print(upload_to_s3('./snapshots.txt','stage.xxxxxxxx.sonartest',s3_key))
