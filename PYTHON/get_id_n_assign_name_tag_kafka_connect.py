import configparser

import boto3

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
#roles = config.sections()
roles = ["xxxxxxxx-sbox-role"]
REGION = "ap-south-1"


def get_kafka_clusters(role_name):
    session = boto3.Session(profile_name=role_name,region_name=REGION)
    client = session.client('kafka')
    response = client.list_clusters()
    return response['ClusterInfoList']


def check_and_assign_name_tag_kafka(cluster_arn, cluster_id, role_name):
    session = boto3.Session(profile_name=role_name,region_name=REGION)
    client = session.client('kafka')

    response = client.list_tags_for_resource(
        ResourceArn=cluster_arn
    )
    tags = response['Tags']

    name_tag_present = 'Name' in tags

    if not name_tag_present:
        print(f"ROLE_NAME: {role_name}\nAssigning Name tag to cluster {cluster_id}\n===================================")
        client.tag_resource(
            ResourceArn=cluster_arn,
            Tags={
                'Name': cluster_id
            }
        )
    else:
        print(f"Name tag already present for cluster {cluster_id}")


def get_kafka_connect_clusters(role_name):
    session = boto3.Session(profile_name=role_name,region_name=REGION)
    client = session.client('kafkaconnect')
    response = client.list_connectors()
    return response['connectors']


def check_and_assign_name_tag_kafka_connect(cluster_arn, cluster_id, role_name):
    session = boto3.Session(profile_name=role_name,region_name=REGION)
    client = session.client('kafkaconnect')

    response = client.list_tags_for_resource(
        resourceArn=cluster_arn
    )
    tags = response['tags']

    name_tag_present = 'Name' in tags

    if not name_tag_present:
        print(f"ROLE_NAME: {role_name}\nAssigning Name tag to cluster {cluster_id}\n===================================")
        client.tag_resource(
            resourceArn=cluster_arn,
            tags={
                'Name': cluster_id
            }
        )
    else:
        print(f"Name tag already present for cluster {cluster_id}")


def main():
    for role in roles:
        kafka_clusters = get_kafka_clusters(role)
        for cluster in kafka_clusters:
            cluster_arn = cluster['ClusterArn']
            cluster_id = cluster['ClusterName']
            check_and_assign_name_tag_kafka(cluster_arn, cluster_id, role)
        connector_cluster = get_kafka_connect_clusters(role)
        for cluster in connector_cluster:
            cluster_arn = cluster['connectorArn']
            cluster_id = cluster['connectorName']
            check_and_assign_name_tag_kafka_connect(cluster_arn, cluster_id,role)


if __name__ == "__main__":
    main()
