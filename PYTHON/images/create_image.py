import boto3
import sys
import time
from botocore.exceptions import ClientError


def get_inst_tag(inst_id, tag_name):
    try:
        response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
        tags = response['Tags']
        for tag in tags:
            if tag['Key'] == tag_name:
                return tag['Value']
        return "NA"
    except ClientError:
        print("Instance Does not exist")
        return


def create_image(instance_id, name):
    response = ec2.create_image(InstanceId=instance_id, NoReboot=True, Name=name)
    print("Got Image ID: ", response["ImageId"])
    return response["ImageId"]


def get_image_status(ami_id):
    response = ec2.describe_images(ImageIds=[ami_id])
    return response["Images"][0]['State']


if len(sys.argv) != 3:
    print("Need instance id and region as args")
else:
    instance_id = sys.argv[1]
    region = sys.argv[2]
    ec2 = boto3.client('ec2', region_name=region)
    instance_name = get_inst_tag(instance_id,"Name")
    timestamp = int(time.time())
    ami_name = f"{instance_name}_Image_{timestamp}"
    ami_id = create_image(instance_id, ami_name)
    ami_state = get_image_status(ami_id)
    while ami_state != "available":
        ami_state = get_image_status(ami_id)
        print(f"Waiting for AMI to be available. Current state: {ami_state}")
        time.sleep(5)
    print("Image created: ", ami_name)
