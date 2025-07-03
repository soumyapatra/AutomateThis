import boto3


def check_bucket_in_backup_policy(bucket_name):
    session = boto3.Session(profile_name="lazypay-prod-role", region_name="ap-south-1")
    backup_client = session.client('backup')
    backup_resource_list = []

    backedup_resources = backup_client.list_protected_resources()
    backup_resource_list.extend(backedup_resources["Results"])
    while "NextToken" in backedup_resources:
        backedup_resources = backup_client.list_protected_resources(NextToken=backedup_resources["NextToken"])
        backup_resource_list.extend(backedup_resources["Results"])

    for item in backup_resource_list:
        if item["ResourceType"] == "S3" and item["ResourceArn"].split(":")[-1] == bucket_name:
            return True
    return False


bucket_name = 'cert-stores'
is_in_backup_policy = check_bucket_in_backup_policy(bucket_name)

if is_in_backup_policy:
    print(f"The bucket '{bucket_name}' is included in an AWS Backup policy.")
else:
    print(f"The bucket '{bucket_name}' is NOT included in any AWS Backup policy.")
