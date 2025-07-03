import re

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import boto3
import re

amis = []
ami_client = boto3.client('ec2',region_name = "ap-southeast-1")
ami_list = ami_client.describe_images(Owners=['self'])

for images in ami_list['Images']:
    amis.append(images['Name'])


query = "prod_rc_fe_limit_service_"
match = process.extractBests(query,amis,score_cutoff=80)
print(match)
