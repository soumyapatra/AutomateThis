import boto3

ec2 = boto3.resource('ec2')

def get_tag(fid):
    ec2instance=ec2.Instance(fid)
    for tags in ec2instance.tags:
        if tags["Key"] == "pt_redis_inst" and tags["Value"] == "hi":
            print "No Tag"
get_tag('i-05c70ec9034456b5b')
