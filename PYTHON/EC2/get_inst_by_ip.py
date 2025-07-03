import boto3

ec2=boto3.resource('ec2')
ip = "10.80.120.80"
for instance in ec2.instances.all():
    if (instance.private_ip_address) == ip:
        print(instance.instance_id,instance.state['Name'])
