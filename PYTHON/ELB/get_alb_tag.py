import boto3



def get_alb_tag(alb_arn,tag_name):
    alb=boto3.client('elbv2')
    response = alb.describe_tags(ResourceArns=[alb_arn])
    tags = response['TagDescriptions'][0]['Tags']
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag["Value"]

print(get_alb_tag('arn:aws:REDACTED','Name'))

