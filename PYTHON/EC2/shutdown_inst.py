import boto3

def instid_tag(tag):
    ec2 = boto3.resource('ec2')
    filters = [{
        'Name': 'tag:{}'.format(tag),
        'Values': ['']
    }]
    instances = ec2.instances.filter(Filters=filters)
    instance_ids = [instance.id for instance in instances]
    return instance_ids
print(instid_tag('pt_tp_redis_inst_2'))
