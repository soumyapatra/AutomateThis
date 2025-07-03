import boto3
from datetime import datetime
import dateparser
ami = boto3.client('ec2')
response = ami.describe_images(ImageIds=['ami-070a6adc2e92b7f1a'])
creation_date = response['Images'][0]['CreationDate']
date1 = dateparser.parse(creation_date)
print(datetime.strftime(date1,'%d %b %Y'))
print(dateparser.parse(creation_date))
