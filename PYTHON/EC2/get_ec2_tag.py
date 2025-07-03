import boto3


def get_inst_tag(tag_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_tags()
    tags = response['Tags']
    for tag in tags:
        if tag['Key'] == tag_name:
            print(tag['Value'])


get_inst_tag('cluster')
