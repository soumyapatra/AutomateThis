import boto3

REGION = 'ap-southeast-1'
cw = boto3.client('cloudwatch', region_name=REGION)
elb_client = boto3.client('elb', region_name=REGION)

SNS_ARN = "arn:aws:REDACTED"

#SNS_ARN = "arn:aws:REDACTED"

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


def get_elb_info():
    response = elb_client.describe_load_balancers()
    lbs = []
    elb_info = []
    lbs.extend(response["LoadBalancerDescriptions"])
    if 'NextMarker' in response:
        response = elb_client.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancerDescriptions"])
    for lb in lbs:
        name = lb["LoadBalancerName"]
        scheme = lb['Scheme']
        tag = get_lb_tag(name)
        elb_info.append({'name': name, 'scheme': scheme, 'tag': tag})

    return elb_info


def get_lb_tag(elb_name):
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


# Backing up OLD alarm names

old_alarms = get_alarm_names()
f = open(alarm_filename, 'a')
for alarm in old_alarms:
    f.write(f'{alarm}\n')
f.close()


# Alarms

def put_elb_latency(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:Latency'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='Latency',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Average',
        Threshold=0.1,
        AlarmDescription='ELB Latency',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_elb_5xx(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:HTTPCode_ELB_5XX'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='HTTPCode_ELB_5XX',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Minimum',
        Threshold=1,
        AlarmDescription='ELB 5xx',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_elb_backend_5xx(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:HTTPCode_Backend_5XX'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='HTTPCode_Backend_5XX',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Minimum',
        Threshold=1,
        AlarmDescription='ELB Backend 5xx',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_elb_unhealthy(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:UnHealthyHostCount'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='UnHealthyHostCount',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Average',
        Threshold=1,
        AlarmDescription='ELB UnHealthyHost',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


# Getting ALB along with TG info

elb_info = get_elb_info()
print(elb_info)
temp_alb_info = [{'name': 'prism-int-elb', 'scheme': 'internal', 'tag': 'RC'}, {'name': 'prism-elb', 'scheme': 'internal', 'tag': 'RC'}]

for elb in elb_info:
    elb_name = elb['name']
    scheme = elb['scheme']
    tag = elb['tag']
    name = f'{tag}:{elb_name}:{scheme}'
    print(name)
    #put_elb_5xx(name, elb_name, SNS_ARN)
    #put_elb_backend_5xx(name, elb_name, SNS_ARN)
    #put_elb_latency(name, elb_name, SNS_ARN)
    #put_elb_unhealthy(name, elb_name, SNS_ARN)
