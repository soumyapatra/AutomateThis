import boto3

def get_instance_name(fid,tagKey):
    # When given an instance ID as str e.g. 'i-1234567', return the instance 'Name' from the name tag.
    ec2 = boto3.resource('ec2')
    ec2instance = ec2.Instance(fid)
    instancename = ''

    for tags in ec2instance.tags:
        if tags["Key"] == '{}'.format(tagKey):
            instancename = tags["Value"]
    return instancename

name_tag=get_instance_name('i-05c70ec9034456b5b','Name')
print ("{}".format(name_tag))
