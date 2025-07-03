import boto3

REGION = 'ap-south-1'
cw = boto3.client('cloudwatch', region_name=REGION)
alb = boto3.client('elbv2', region_name=REGION)

SNS_ARN = "arn:aws:REDACTED"

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
        scheme = lb['Scheme']
        if get_trgt_arn(name):
            tg_arn = get_trgt_arn(name)
            lb_arn = name.split(':')[-1]
            tag = get_lb_tag(name)
            lb_arn = lb_arn.replace('loadbalancer/', '')
            alb_names.append({'alb': lb_arn, "tg": tg_arn, "tag": tag, "scheme": scheme})
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


# Alarms

def put_4xx_alb_alarm(name, tg_arn, alb_arn, sns_arn):
    alarm_name = f'{name}:HTTPCode_Target_4XX_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='HTTPCode_Target_4XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Minimum',
        Threshold=1,
        AlarmDescription='ALB 4XX Alarm',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_arn
            },
            {
                'Name': 'TargetGroup',
                'Value': tg_arn
            }
        ])
    return response


def put_5xx_alb_target_alarm(name, tg_arn, alb_arn, sns_arn):
    alarm_name = f'{name}:HTTPCode_Target_5XX_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='HTTPCode_Target_5XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Minimum',
        Threshold=1,
        AlarmDescription='ALB 5XX Alarm',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_arn
            },
            {
                'Name': 'TargetGroup',
                'Value': tg_arn
            }
        ])
    return response





# Getting ALB along with TG info

alb_info = get_alb_info()

# temp_albdd_info = [{'alb': 'app/fusionproxy-ext2-alb/96805b161e40b2ae', 'tg': ['targetgroup/falcon-tg/7ffdc7ff1f42e089', 'targetgroup/fusionproxy-80-tg/83cb438d14597da0'], 'tag': 'RC', 'scheme': 'internet-facing'},{'alb': 'app/ft-prod-nae-kinesis-priv-alb/29d86f3dacf77415', 'tg': 'targetgroup/ft-prod-nae-kinesis-tg/22d38214ae260954', 'tag': 'Reverie', 'scheme': 'internal'}]

for alb in alb_info:
    alb_arn = alb['alb']
    tg_arn = alb['tg']
    tag = alb['tag']
    scheme = alb['scheme']
    alb_name = alb_arn.split('/')[1]
    if isinstance(tg_arn, list) and len(tg_arn) > 1:
        for tg in tg_arn:
            tg_name = tg.split('/')[1]
            name = f'{tag}:{alb_name}:{scheme}'
            name_with_tg = f'{tag}:{alb_name}:{tg_name}:{scheme}'
            print(name_with_tg, name_with_tg, alb_arn, tg)
            #put_4xx_alb_alarm(name, tg, alb_arn, SNS_ARN)
            #put_5xx_alb_target_alarm(name, tg, alb_arn, SNS_ARN)
    else:
        tg_name = tg_arn.split('/')[1]
        name = f'{tag}:{alb_name}:{scheme}'
        name_with_tg = f'{tag}:{alb_name}:{tg_name}:{scheme}'
        # print(name, name_with_tg, alb_arn, tg_arn)
        #put_4xx_alb_alarm(name, tg_arn, alb_arn, SNS_ARN)
        #put_5xx_alb_target_alarm(name, tg_arn, alb_arn, SNS_ARN)
