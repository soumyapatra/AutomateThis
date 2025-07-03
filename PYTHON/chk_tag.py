import boto3

ec2 = boto3.resource('ec2')

def chk_inst_tag(fid,tagKey):
    ec2inst=ec2.Instance(fid)
    inst_tag=""
    for tag in ec2inst.tags:
        if tag["Key"] == "{}".format(tagKey):
            return tag["Value"] 

tag=chk_inst_tag('i-05c70ec9034456b5b','pt_tp123')
print ("{}".format(tag))

if tag == "":
    print ("It's Empty")
elif tag is None:
    print ("It's None")
   
