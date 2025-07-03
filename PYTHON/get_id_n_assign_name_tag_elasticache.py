import configparser

import boto3

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
roles = config.sections()


def get_elasticache_clusters(role_name):
    session = boto3.Session(profile_name=role_name, region_name="ap-south-1")
    client = session.client('elasticache')
    response = client.describe_cache_clusters()
    return response['CacheClusters']


def check_and_assign_name_tag(cluster_id, role_name, region="ap-south-1"):
    try:
        session = boto3.Session(profile_name=role_name, region_name=region)
        client = session.client('elasticache')
        account_id = session.client('sts').get_caller_identity().get('Account')
        response = client.list_tags_for_resource(
            ResourceName=f'arn:aws:REDACTED'
        )
        tags = response['TagList']
        name_tag_present = any(tag['Key'] == 'Name' for tag in tags)

        if not name_tag_present:
            print(f"Assigning Name tag to cluster {cluster_id}")
            client.add_tags_to_resource(
                ResourceName=f'arn:aws:REDACTED',
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': cluster_id
                    }
                ]
            )
        else:
            print(f"Name tag already present for cluster {cluster_id}")
    except Exception as e:
        print(f"Got Error for cluster: {cluster_id} for role {role_name}:\n{e}\n")
        return


def main():
    for role in roles:
        clusters = get_elasticache_clusters(role)
        for cluster in clusters:
            cluster_id = cluster['CacheClusterId']
            check_and_assign_name_tag(cluster_id, role)


if __name__ == "__main__":
    main()
