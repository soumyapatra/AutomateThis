"""
Author: Soumyaranjan Patra(soumyapatra9403@gmail.com)
This script is used for creating CSV file(missing_tags.csv) which can
be opened in Google Sheet for checking the Resources with missing required
tags. This can be used with script read_csv_n_apply_tags.py after adding
the required tag key as column and row as tag value.
Sample doc: https://docs.google.com/spreadsheets/d/1VlxoBAhjgDQuKvsCyFMlgJGT9_VvNpEt4zX2WOJnK1E/edit?gid=2120131686#gid=2120131686
This script uses all the AWS roles mentioned in AWS profile file of the current
user.
This script may require updated python modules. Hence, adding steps for the same:
#virtualenv venv3 (created python virtualenv)
#source venv3/bin/activate (activates created python env)
#pip install -r requirements.txt (install required modules in current env)
And after this run script in this env normally as
#python missing_tags.py
or use python bin the virtualenv bin folder when not in env
for running this script
#./venv3/bin/python missing_tags.csv
USAGE:
python missing_tags.py
"""
import configparser
import os
import boto3
import pandas as pd

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

required_tags = ["Name", "clusters", "service", "owner", "requestedby", "env", "createdby", "component", "vertical",
                 "subvertical"]

required_tags_colums = {tag: "" for tag in required_tags}
print(required_tags_colums)

missing_tags_data = []

for role in roles:
    print(f"Working on role: {role}")
    session = boto3.Session(profile_name=role, region_name="ap-south-1")
    rds_client = session.client("rds")
    response = rds_client.describe_db_instances()["DBInstances"]
    acct_name = role.rsplit("-", 1)[0]
    account_id = session.client('sts').get_caller_identity().get('Account')
    for instance in response:
        instance_id = instance['DBInstanceIdentifier']
        resource_arn = instance['DBInstanceArn']
        tags = rds_client.list_tags_for_resource(
            ResourceName=f'{resource_arn}'
        )['TagList']

        tag_keys = [tag['Key'] for tag in tags]

        missing_tags = [tag for tag in required_tags if tag not in tag_keys]

        if missing_tags:
            missing_tags_dict = {
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': "RDS",
                'Resource ID': instance_id,
                'Missing Tags': ' | '.join(missing_tags)
            }
            missing_tags_dict.update(required_tags_colums)
            missing_tags_data.append(missing_tags_dict)

    kafka_client = session.client('kafka')
    kafka_clusters = kafka_client.list_clusters()['ClusterInfoList']
    for cluster in kafka_clusters:
        cluster_arn = cluster['ClusterArn']
        cluster_name = cluster['ClusterName']
        tags = kafka_client.list_tags_for_resource(
            ResourceArn=cluster_arn
        )['Tags']
        tag_keys = tags.keys()
        missing_tags = [tag for tag in required_tags if tag not in tag_keys]
        if missing_tags:
            missing_tags_dict = {
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': 'Kafka',
                'Resource ID': cluster_name,
                'Missing Tags': ' | '.join(missing_tags)
            }
            missing_tags_dict.update(required_tags_colums)
            missing_tags_data.append(missing_tags_dict)
    kafka_connect_client = session.client('kafkaconnect')
    connectors = kafka_connect_client.list_connectors()['connectors']

    for connector in connectors:
        connector_arn = connector['connectorArn']
        connector_name = connector['connectorName']

        tags = kafka_connect_client.list_tags_for_resource(
            resourceArn=connector_arn
        )['tags']

        tag_keys = tags.keys()

        missing_tags = [tag for tag in required_tags if tag not in tag_keys]

        if missing_tags:
            missing_tags_dict = {
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': 'Kafka Connector',
                'Resource ID': connector_name,
                'Missing Tags': ' | '.join(missing_tags)
            }
            missing_tags_dict.update(required_tags_colums)
            missing_tags_data.append(missing_tags_dict)
    elasticache_client = session.client('elasticache')
    cache_clusters = elasticache_client.describe_cache_clusters()['CacheClusters']

    for cluster in cache_clusters:
        cluster_arn = cluster['ARN']
        cluster_id = cluster['CacheClusterId']

        tags = elasticache_client.list_tags_for_resource(
            ResourceName=cluster_arn
        )['TagList']

        tag_keys = [tag['Key'] for tag in tags]

        missing_tags = [tag for tag in required_tags if tag not in tag_keys]

        if missing_tags:
            missing_tags_dict = {
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': 'ElastiCache',
                'Resource ID': cluster_id,
                'Missing Tags': ' | '.join(missing_tags)
            }
            missing_tags_dict.update(required_tags_colums)
            missing_tags_data.append(missing_tags_dict)

    ec2_client = session.client('ec2')
    ec2_instances = ec2_client.describe_instances()['Reservations']

    for reservation in ec2_instances:
        for instance in reservation['Instances']:
            tags = instance.get('Tags', [])
            instance_id = instance['InstanceId']
            instance_name = next((tag['Value'] for tag in tags if tag['Key'] == 'Name'), instance_id)

            tags = instance.get('Tags', [])

            tag_keys = [tag['Key'] for tag in tags]

            missing_tags = [tag for tag in required_tags if tag not in tag_keys]

            if missing_tags:
                missing_tags_dict = {
                    'Account Name': acct_name,
                    'Account Id': account_id,
                    'Resource Type': 'EC2 Instance',
                    'Resource ID': f"{instance_name}({instance_id})",
                    'Missing Tags': ' | '.join(missing_tags)
                }
                missing_tags_dict.update(required_tags_colums)
                missing_tags_data.append(missing_tags_dict)

df = pd.DataFrame(missing_tags_data)

df.to_csv('missing_tags.csv', index=False)

print("Exported to missing_tags.csv")
