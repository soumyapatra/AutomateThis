import boto3

ec2 = boto3.resource('ec2')

def check_tag(fid,tagKey):
    ec2instance=ec2.Instance(fid)
    for tags in ec2instance.tags:
        print("{}".format(tagKey))
        if tags["Key"] == "{}".format(tagKey):
            return tags["Value"]

check_tag('i-05c70ec9034456b5b','Name')
