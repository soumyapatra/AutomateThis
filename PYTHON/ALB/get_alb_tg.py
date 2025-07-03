""""""
import boto3

REGION = 'ap-southeast-1'
cw = boto3.client('cloudwatch', region_name=REGION)
alb = boto3.client('elbv2', region_name=REGION)

alarm_filename = "./old_alb_alarms.txt"

alias_dict = {'rc_production': 'RC', 'reverie_production': 'Reverie'}


def get_alarm_names():
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    alarm_name = []
    for alarm in alarms:
        if alarm['Namespace'] == 'AWS/ELB' or alarm['Namespace'] == 'AWS/ApplicationELB':
            name = alarm['AlarmName']
            alarm_name.append(name)
    return alarm_name


def get_trgt_arn(lb_arn):
    response = alb.describe_target_groups(
        LoadBalancerArn=lb_arn)
    if len(response['TargetGroups']) == 0:
        return False
    elif len(response['TargetGroups']) > 1:
        targets = response['TargetGroups']
        tg_arn = []
        for target in targets:
            tg = target['TargetGroupArn'].split(':')[-1]
            tg_arn.append(tg)
        return tg_arn
    tg_arn = response["TargetGroups"][0]["TargetGroupArn"]
    return tg_arn.split(':')[-1]


def get_alb_info():
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancers"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        name = lb["LoadBalancerArn"]
        if get_trgt_arn(name):
            tg_arn = get_trgt_arn(name)
            lb_arn = name.split(':')[-1]
            tag = get_lb_tag(name)
            lb_arn = lb_arn.replace('loadbalancer/', '')
            alb_names.append({'alb': lb_arn, "tg": tg_arn, "tag": tag})
    return alb_names


def get_lb_tag(alb_arn):
    response = alb.describe_tags(ResourceArns=[alb_arn])
    tags = response['TagDescriptions'][0]['Tags']
    if len(tags) == 0:
        return "NA"
    else:
        for tag in tags:
            if tag['Key'] == "billing_unit":
                value = tag['Value']
                return alias_dict[value]
    return "NA"


# Backing up OLD alarm names

old_alarms = get_alarm_names()
f = open(alarm_filename, 'a')
for alarm in old_alarms:
    f.write(f'{alarm}\n')
f.close()

# Getting ALB along with TG info

alb_info = get_alb_info()

for alb in alb_info:
    alb_arn = alb['alb']
    tg_arn = alb['tg']
    tag = alb['tag']
    print(alb_arn, tg_arn, tag)
