import boto3
import pandas as pd

role = "sbox-role"
session = boto3.Session(profile_name=role, region_name="ap-south-1")
client = session.client('rds')
rds_resources = client.describe_db_instances()['DBInstances']

required_tags = ["Name", "clusters", "service", "owner", "requestedby", "env", "createdby", "component", "vertical",
                 "subvertical"]
response = client.describe_db_instances()

missing_tags_data = []

for instance in response['DBInstances']:
    instance_id = instance['DBInstanceIdentifier']
    resource_arn = instance['DBInstanceArn']

    tags = client.list_tags_for_resource(
        ResourceName=f'{resource_arn}'
    )['TagList']

    tag_keys = [tag['Key'] for tag in tags]

    missing_tags = [tag for tag in required_tags if tag not in tag_keys]

    if missing_tags:
        missing_tags_data.append({
            'RDS Instance ID': instance_id,
            'Missing Tags': ', '.join(missing_tags)
        })

df = pd.DataFrame(missing_tags_data)

df.to_csv('missing_tags.csv', index=False)

print("Exported to missing_tags.csv")
