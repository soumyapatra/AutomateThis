import boto3

REGION = 'ap-southeast-1'


def get_lb(region):
    elb = boto3.client('elb', region_name=region)
    response = elb.describe_load_balancers()
    lbs = []
    elb_names = []
    lbs.extend(response["LoadBalancerDescriptions"])
    if 'NextMarker' in response:
        response = elb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancerDescriptions"])
    for lb in lbs:
        elb_names.append(lb["LoadBalancerName"])
    return elb_names


def get_alb(region):
    alb = boto3.client('elbv2', region_name=region)
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancers"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        name = lb["LoadBalancerArn"]
        lb_arn = name.split(':')[-1]
        lb_arn = lb_arn.replace('loadbalancer/', '')
        alb_names.append(lb_arn)
    return alb_names


elb = get_lb(REGION)
alb = get_alb(REGION)


def get_alarm_names(region, elb, alb):
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        for dimension in alarm['Dimensions']:
            if dimension['Name'] == "LoadBalancer":
                if dimension['Value'] in alb:
                    alb.remove(dimension['Value'])
            elif dimension['Name'] == "LoadBalancerName":
                if dimension['Value'] in elb:
                    elb.remove(dimension['Value'])


get_alarm_names(REGION, elb, alb)
print(alb)
print(elb)
