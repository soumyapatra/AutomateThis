import boto3
import re

ec2 = boto3.client('ec2')

response = ec2.describe_flow_logs()
eni_chk = re.compile("^eni-\w*")
vpc_chk = re.compile("^vpc-\w*")


def desc_eni(eni):
    response = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni])
    status = response['NetworkInterfaces'][0]['Status']
    if status == "available":
        return f'ENI: {eni} not in use'
    return response['NetworkInterfaces'][0]['Attachment']['InstanceId']


def desc_vpc(vpc_id):
    response = ec2.describe_vpcs(VpcIds=[vpc_id])
    print(response['Vpcs']['CidrBlock'])


for logs in response['FlowLogs']:
    rsc_id = logs['ResourceId']
    if eni_chk.match(rsc_id):
        print(desc_eni(rsc_id), "\n")
    elif vpc_chk.match(rsc_id):
        print(desc_vpc(rsc_id))
