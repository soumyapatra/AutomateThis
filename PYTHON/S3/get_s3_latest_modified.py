import boto3

role = "lazypay-prod-role"
session = boto3.Session(profile_name=role, region_name="ap-south-1")


def get_latest_object(bucket_name):
    s3 = session.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)

    if 'Contents' in response:
        # Get the latest object by sorting the list by LastModified field
        latest_obj = max(response['Contents'], key=lambda x: x['LastModified'])
        return latest_obj['Key'], latest_obj['LastModified']
    else:
        return None, None


bucket_name = 'lazypay-prod-s3-buckets-continuous-buckup-hyd '
latest_key, latest_modification = get_latest_object(bucket_name)

if latest_key:
    print(f"Latest object: {latest_key} was modified on {latest_modification}")
else:
    print("No objects found in the bucket.")
