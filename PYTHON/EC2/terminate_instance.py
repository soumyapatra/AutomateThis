import boto3
from botocore.exceptions import ClientError

REGION = "ap-south-1"

filename = "./instances.txt"

ec2 = boto3.client("ec2", region_name=REGION)


def return_state(inst_id):
    try:
        response = ec2.describe_instance_status(
            InstanceIds=[inst_id], IncludeAllInstances=True
        )
        state = response["InstanceStatuses"][0]["InstanceState"]["Name"]
        return state
    except ClientError as e:
        print("Could not find instance", "Details: ", e)
        return False


def terminate_instance(inst_id):
    try:
        response = ec2.terminate_instances(
            InstanceIds=[inst_id]
        )
        return response
    except ClientError as e:
        print("Could not delete instance", "Details: ", e)
        return False


with open(filename) as f:
    lines = [line.strip() for line in f]

# f = open(filename, "r")
for i in lines:
    if return_state(i):
        instance_state = return_state(i)
        if instance_state == "stopped":
            print("terminating instance", i, "with instance state", instance_state)
            terminate_instance(i)
        else:
            print("Instance is not in stopped state: ", i)
