import boto3
import csv
import configparser
import os

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()


def is_graviton(instance_type):
    graviton_types = ['a1', 'c6g', 'm6g', 'r6g', 't4g']
    for g_type in graviton_types:
        if instance_type.startswith(g_type):
            return "Yes"
    return "No"


csv_file_name = 'ec2_instances.csv'
csv_columns = ['Account Name', 'Instance ID', 'Instance Type', 'Is Graviton', 'Service Tag', 'Name Tag']
instance_data = []

for role in roles:
    session = boto3.Session(profile_name=role, region_name='ap-south-1')  # Specify your AWS region
    ec2 = session.client('ec2')
    acct_name = role.rsplit("-", 1)[0]
    paginator = ec2.get_paginator('describe_instances')
    page_iterator = paginator.paginate()
    for page in page_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                graviton = is_graviton(instance_type)
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                service_tag = tags.get('service', 'N/A')  # Change 'Service' to your actual service tag key
                name_tag = tags.get('Name', 'N/A')
                instance_info = {
                    'Account Name': acct_name,
                    'Instance ID': instance_id,
                    'Instance Type': instance_type,
                    'Is Graviton': graviton,
                    'Service Tag': service_tag,
                    'Name Tag': name_tag
                }
                instance_data.append(instance_info)

try:
    with open(csv_file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in instance_data:
            writer.writerow(data)
    print(f"Data successfully written to {csv_file_name}")
except IOError:
    print("I/O error when writing to CSV")
