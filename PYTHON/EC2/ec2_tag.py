import boto3


def get_tag(inst_id, tag_name):
    ec2_client = boto3.resource('ec2')
    ec2_instance = ec2_client.Instance(inst_id)
    for tags in ec2_instance.tags:
        if tags["Key"] == tag_name:
            return tags["Value"]


print(get_tag("i-0d391ad09539a2bb5", "Name"))
