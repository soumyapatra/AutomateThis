import boto3 

def get_inst_state(inst_id):
    ec2=boto3.client('ec2')
    response=ec2.describe_instances(InstanceIds=[inst_id])
    return response['Reservations'][0]['Instances'][0]['State']['Name']


print(get_inst_state('i-03f07aa521217e6a6'))



def get_inst_state_status(inst_id):
    ec2=boto3.client('ec2')
    response=ec2.describe_instance_status(InstanceIds=[inst_id])
    return response['InstanceStatuses'][0]['InstanceState']['Name']


print(get_inst_state_status('i-02fe85f2e0bd52f9f'))

