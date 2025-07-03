import configparser

import boto3
import csv

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
roles = config.sections()


def get_ec2_tags(client):
    ec2_tags = []
    response = client.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            tags = instance.get('Tags', [])
            for tag in tags:
                ec2_tags.append(['EC2', instance_id, tag['Key'], tag['Value']])
    return ec2_tags


def get_rds_tags(client):
    rds_tags = []
    response = client.describe_db_instances()
    for db_instance in response['DBInstances']:
        db_instance_id = db_instance['DBInstanceIdentifier']
        tags_response = client.list_tags_for_resource(ResourceName=db_instance['DBInstanceArn'])
        tags = tags_response.get('TagList', [])
        for tag in tags:
            rds_tags.append(['RDS', db_instance_id, tag['Key'], tag['Value']])
    return rds_tags


def get_kafka_tags(client):
    kafka_tags = []
    response = client.list_clusters()
    for cluster in response['ClusterInfoList']:
        cluster_arn = cluster['ClusterArn']
        tags_response = client.list_tags_for_resource(ResourceArn=cluster_arn)
        tags = tags_response.get('Tags', {})
        for key, value in tags.items():
            kafka_tags.append(['Kafka', cluster_arn, key, value])
    return kafka_tags


def get_kafka_connect_tags(client):
    kafka_connect_tags = []
    response = client.list_connectors()
    for connector in response['Connectors']:
        connector_arn = connector['ConnectorArn']
        tags_response = client.list_tags_for_resource(ResourceArn=connector_arn)
        tags = tags_response.get('Tags', {})
        for key, value in tags.items():
            kafka_connect_tags.append(['Kafka Connect', connector_arn, key, value])
    return kafka_connect_tags


def get_elasticache_tags(client):
    elasticache_tags = []
    response = client.describe_cache_clusters()
    for cluster in response['CacheClusters']:
        cluster_id = cluster['CacheClusterId']
        tags_response = client.list_tags_for_resource(ResourceName=cluster['ARN'])
        tags = tags_response.get('TagList', [])
        for tag in tags:
            elasticache_tags.append(['ElastiCache', cluster_id, tag['Key'], tag['Value']])
    return elasticache_tags


def main():
    ec2_client = boto3.client('ec2')
    rds_client = boto3.client('rds')
    kafka_client = boto3.client('kafka')
    kafka_connect_client = boto3.client('kafkaconnect')
    elasticache_client = boto3.client('elasticache')

    all_tags = []
    all_tags.extend(get_ec2_tags(ec2_client))
    all_tags.extend(get_rds_tags(rds_client))
    all_tags.extend(get_kafka_tags(kafka_client))
    all_tags.extend(get_kafka_connect_tags(kafka_connect_client))
    all_tags.extend(get_elasticache_tags(elasticache_client))

    with open('aws_tags.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Service', 'Resource ID', 'Tag Key', 'Tag Value'])
        csvwriter.writerows(all_tags)


if __name__ == "__main__":
    main()
