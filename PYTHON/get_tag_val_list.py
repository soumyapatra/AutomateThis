import configparser
import boto3

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
roles = config.sections()

vertical_tag_list = ["CL", "datascience", "PTE", "TC", "TM"]


def get_unique_tag_values(tag_key, role_name):
    session = boto3.Session(profile_name=role_name, region_name="ap-south-1")

    ec2_client = session.client('ec2')

    response = ec2_client.describe_instances()

    tag_values = set()

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == tag_key:
                        if tag["Value"] not in vertical_tag_list:
                            tag_val = tag["Value"]
                            print(f"Role Name: {role_name}\nInstance Id: {instance_id}\nTAG: {tag_key}={tag_val}")

    return list(tag_values)


tag_key = 'vertical'
for role in roles:
    get_unique_tag_values(tag_key, role)
