import boto3
from datetime import datetime

import dateparser



ami = boto3.client('ec2')
response = ami.describe_images(Owners=['self'])

amis = response['Images']

#print(amis)
ami_list = []
for ami in amis:
    ami_list.append(tuple([ami['ImageId'],ami['Name'],ami['CreationDate']]))

print(ami_list)
