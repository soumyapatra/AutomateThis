import re
from datetime import datetime
import boto3
import dateparser


REGION = 'ap-south-1'
ami_client = boto3.client('ec2', region_name=REGION)
response = ami_client.describe_images(Owners=['self'])


for ami in response['Images']:
    parsed_date = dateparser.parse(ami['CreationDate'])
    date = datetime.strftime(parsed_date, '%d %b %Y %H:%M:%S')
    print(f'{parsed_date}   ==    {date}')
