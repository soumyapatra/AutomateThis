import configparser
import boto3

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
roles = config.sections()


def list_msk_broker_dns(role_name):
    session = boto3.Session(profile_name=role_name, region_name="ap-south-1")
    client = session.client('kafka')

    response = client.list_clusters()

    for cluster_info in response['ClusterInfoList']:
        cluster_arn = cluster_info['ClusterArn']
        cluster_name = cluster_info['ClusterName']

        bkr_response = client.get_bootstrap_brokers(
            ClusterArn=cluster_arn
        )
        brokers = bkr_response["BootstrapBrokerString"]
        print(f"Cluster Name: {cluster_name}")
        print(f"Cluster ARN: {cluster_arn}")
        print(f"Cluster Broker: {brokers}")


if __name__ == "__main__":
    for role in roles:
        list_msk_broker_dns(role)