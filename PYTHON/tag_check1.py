import boto3

ec2 = boto3.resource('ec2')

def check_tag(fid):
    ec2instance=ec2.Instance(fid)
    for tag in ec2instance.tags:
    	tag_key = input("Enter TAG: ")
        if tag["Key"] == "{tag_key}" and tag["Value"] == "":
            print("Tag is Empty")
        else:
            print ("Tag Present")
            
check_tag('i-05c70ec9034456b5b')
