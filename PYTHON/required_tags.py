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
            missing_tags_data.append({
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': "RDS",
                'Resource ID': instance_id,
                'Missing Tags': ' | '.join(missing_tags)
            })

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
            missing_tags_data.append({
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': 'Kafka',
                'Resource ID': cluster_name,
                'Missing Tags': ' | '.join(missing_tags)
            })
    kafka_connect_client = session.client('kafkaconnect')
    connectors = kafka_connect_client.list_connectors()['connectors']

    for connector in connectors:
        connector_arn = connector['connectorArn']
        connector_name = connector['connectorName']

        tags = kafka_connect_client.list_tags_for_resource(
            resourceArn=connector_arn
        )['tags']

        # Extract tag keys
        tag_keys = tags.keys()

        # Check for missing tags
        missing_tags = [tag for tag in required_tags if tag not in tag_keys]

        if missing_tags:
            missing_tags_data.append({
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': 'Kafka Connector',
                'Resource ID': connector_name,
                'Missing Tags': ' | '.join(missing_tags)
            })
    elasticache_client = session.client('elasticache')
    cache_clusters = elasticache_client.describe_cache_clusters()['CacheClusters']

    for cluster in cache_clusters:
        cluster_arn = cluster['ARN']
        cluster_id = cluster['CacheClusterId']

        # Get tags for the ElastiCache cluster
        tags = elasticache_client.list_tags_for_resource(
            ResourceName=cluster_arn
        )['TagList']

        # Extract tag keys
        tag_keys = [tag['Key'] for tag in tags]

        # Check for missing tags
        missing_tags = [tag for tag in required_tags if tag not in tag_keys]

        if missing_tags:
            missing_tags_data.append({
                'Account Name': acct_name,
                'Account Id': account_id,
                'Resource Type': 'ElastiCache',
                'Resource ID': cluster_id,
                'Missing Tags': ' | '.join(missing_tags)
            })

    ec2_client = session.client('ec2')
    ec2_instances = ec2_client.describe_instances()['Reservations']

    for reservation in ec2_instances:
        for instance in reservation['Instances']:
            tags = instance.get('Tags', [])
            instance_id = instance['InstanceId']
            instance_name = next((tag['Value'] for tag in tags if tag['Key'] == 'Name'), instance_id)

            # Get tags for the EC2 instance
            tags = instance.get('Tags', [])

            # Extract tag keys
            tag_keys = [tag['Key'] for tag in tags]

            # Check for missing tags
            missing_tags = [tag for tag in required_tags if tag not in tag_keys]

            if missing_tags:
                missing_tags_data.append({
                    'Account Name': acct_name,
                    'Account Id': account_id,
                    'Resource Type': 'EC2 Instance',
                    'Resource ID': instance_name,
                    'Missing Tags': ', '.join(missing_tags)
                })

df = pd.DataFrame(missing_tags_data)

df.to_csv('missing_tags.csv', index=False)

print("Exported to missing_tags.csv")
