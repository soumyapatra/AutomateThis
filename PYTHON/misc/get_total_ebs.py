import boto3

ec2 = boto3.resource('ec2')
response = ec2.instances.filter(Filters=[{'Name': 'tag:billing_unit', 'Values': ['rc_stage']}])

f = open("/tmp/EBSSum_report2.csv", "w")
f.write("Instance_id, Instance_name, Instance_type, Private_IP, EBS_sum")
f.write("\n")
f.close()

for instance in response:
    sum = 0
    instance_name = "NA"
    volumes = instance.volumes.all()
    id = instance.instance_id
    type = instance.instance_type
    ip = instance.private_ip_address
    for volume in volumes:
        sum = sum + volume.size
    for tags in instance.tags:
        if tags["Key"] == 'Name':
            instance_name = tags["Value"]
    f = open("/tmp/EBSSum_report2.csv", "a")
    f.write(f'{id},{instance_name},{type},{ip},{sum}')
    f.write("\n")
    f.close()
