import boto3


def get_inst_name(tag_key):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(Filters=[], InstanceIds=['i-ca3f706e'])
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    for tag in tags:
        if tag['Key'] == tag_key:
            print(tag['Value'])


get_inst_name()
