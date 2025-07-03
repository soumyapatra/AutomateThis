import boto3
import os
import json
import csv
from datetime import datetime
from datetime import date






def get_lb(region):
    elb=boto3.client('elb',region_name=region)
    response=elb.describe_load_balancers()
    lbs=[]
    elb_names=[]
    lbs.extend(response["LoadBalancerDescriptions"])
    if 'NextMarker' in response:
        response = elb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancerDescriptions"])
    for lb in lbs:
        elb_names.append(lb["LoadBalancerName"])
    return elb_names


def get_alb(region):
    alb = boto3.client('elbv2',region_name=region)
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancers"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        alb_names.append(lb["LoadBalancerArn"])
    return alb_names



def get_alb_log(arn):
    alb=boto3.client('elbv2')
    response=alb.describe_load_balancer_attributes(LoadBalancerArn=arn)
    s3_bucket = ""
    s3_prefix= ""
    for keys in response['Attributes']:
        if keys['Key'] == 'access_logs.s3.enabled' and keys['Value'] == 'false':
            return "NA"
        elif keys['Key'] == 'access_logs.s3.bucket':
            s3_bucket = keys['Value']
        elif keys['Key'] == 'access_logs.s3.prefix':
            s3_prefix = keys['Value']
    return f'{s3_bucket}/{s3_prefix}'


get_alb_log('aws-arn')


albs=get_alb('ap-southeast-1')
alb_log_list=[]
for alb in albs:
    alb_name=alb.split('/')[-2]
    s3_log=get_alb_log(alb)
    alb_log_list.append({'alb':alb_name,'log_location':s3_log})

print(alb_log_list)
