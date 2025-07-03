from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import boto3
amis = []
ami_client = boto3.client('ec2',region_name = "ap-southeast-1")
ami_list = ami_client.describe_images(Owners=['self'])

for images in ami_list['Images']:
    amis.append(images['Name'])
query = "prod.xxxxxxxxxx_rummy"
#print(process.extractOne(query,amis))
#print(process.extract(query,amis))
print(process.extractBests(query,amis,score_cutoff=90))
