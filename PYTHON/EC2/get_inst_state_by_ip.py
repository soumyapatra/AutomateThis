import boto3


def get_instance_state(ip):

    ec2 = boto3.resource('ec2',region_name='ap-southeast-1')
    for instance in ec2.instances.all():
        if (instance.private_ip_address) == ip:
            return instance.state['Name']

ip="10.80.120.80"
print(get_instance_state(ip))
