import boto3

ec2=boto3.client('ec2')

def get_add(x):
    response = ec2.describe_addresses(AllocationIds=[x])
    for add in response["Addresses"]:
        return add["AllocationId"]


def chk_add(x):
    response=ec2.describe_addresses(AllocationIds=[x])
    for add in response["Addresses"]:
        if "AssociationId" not in add:
            return True
        else:
            return False

def chk_all_add():
    response = ec2.describe_addresses()
    for address in response["Addresses"]:
        print(address["AllocationId"])
print(chk_all_add())
