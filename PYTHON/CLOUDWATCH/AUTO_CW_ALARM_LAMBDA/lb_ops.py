import boto3
import os

REGION = os.environ['REGION']

alb_client = boto3.client('elbv2', region_name=REGION)
elb_client = boto3.client('elb', region_name=REGION)

alias_dict = {'rc_production': 'RC', 'reverie_production': 'Reverie'}


def get_trgt_arn(lb_arn):
    response = alb_client.describe_target_groups(
        LoadBalancerArn=lb_arn)
    tg_list = []
    for tg in response['TargetGroups']:
        tg_list.append(tg['TargetGroupArn'].split(':')[-1])
    if len(tg_list) != 0:
        return tg_list
    else:
        return False


def get_alb_info(alb_arn):
    response = alb_client.describe_load_balancers(LoadBalancerArns=[alb_arn])
    alb_info = response['LoadBalancers'][0]
    scheme = alb_info['Scheme']
    tag = get_alb_tag(alb_arn)
    lb_arn = alb_arn.split(':')[-1]
    lb_arn = lb_arn.replace('loadbalancer/', '')
    alb_name = lb_arn.split('/')[1]
    lb_info = {'alb_arn': lb_arn, 'alb_name': alb_name, "tag": tag, "scheme": scheme}
    return lb_info


def get_alb_tag(alb_arn):
    response = alb_client.describe_tags(ResourceArns=[alb_arn])
    tags = response['TagDescriptions'][0]['Tags']
    if len(tags) == 0:
        return "NA"
    else:
        for tag in tags:
            if tag['Key'] == "billing_unit":
                value = tag['Value']
                if value in alias_dict:
                    return alias_dict[value]
    return "NA"


# Getting ELB Info

def get_elb_tag(elb_name):
    response = elb_client.describe_tags(LoadBalancerNames=[elb_name])
    tags = response['TagDescriptions'][0]['Tags']
    if len(tags) == 0:
        return "NA"
    else:
        for tag in tags:
            if tag['Key'] == "billing_unit":
                value = tag['Value']
                return alias_dict[value]
    return "NA"


def get_elb_info(elb):
    response = elb_client.describe_load_balancers(LoadBalancerNames=[elb])
    info = response['LoadBalancerDescriptions'][0]
    scheme = info['Scheme']
    tag = get_elb_tag(elb)
    elb_info = {'scheme': scheme, 'tag': tag}
    return elb_info


def get_alarm_names(lb_name, lb_type):
    cw = boto3.client('cloudwatch', region_name=REGION)
    alarms = []
    names = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    if lb_type == "alb":
        for alarm in alarms:
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "LoadBalancer" and dimension["Value"] == lb_name:
                    names.append(alarm["AlarmName"])
    elif lb_type == "elb":
        for alarm in alarms:
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "LoadBalancerName" and dimension["Value"] == lb_name:
                    names.append(alarm["AlarmName"])
    return names
