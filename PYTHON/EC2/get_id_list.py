import boto3

def get_inst_list():
    ec2=boto3.resource('ec2')
    instances=ec2.instances.filter()
    inst_ids=[]
    for instance in instances:
        inst_ids.append(instance.id)
    return inst_ids

print(get_inst_list())
