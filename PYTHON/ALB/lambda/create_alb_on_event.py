"""
Lambda Script for Creating ALB related Alarms based LB creation Event
"""
import json
import os
import boto3

REGION = os.environ['REGION']
SNS_ARN = os.environ['SNS_ARN']
ENV = os.environ['ENV']
ALERT_SNS_ARN = os.environ['ALERT_SNS_ARN']

cw = boto3.client('cloudwatch')
alb_client = boto3.client('elbv2', region_name=REGION)
elb_client = boto3.client('elb', region_name=REGION)
alias_dict = {'rc_production': 'RC', 'reverie_production': 'Reverie'}


# Getting Alb Info

def get_target_arn(lb_arn):
    """Get ALB target groups"""
    response = alb_client.describe_target_groups(
        LoadBalancerArn=lb_arn)
    tg_arn = response["TargetGroups"][0]["TargetGroupArn"]
    return tg_arn.split(':')[-1]


def get_alb_info(alb_arn):
    """Get Alb info"""
    response = alb_client.describe_load_balancers(LoadBalancerArns=[alb_arn])
    alb_info = response['LoadBalancers'][0]
    scheme = alb_info['Scheme']
    tag = get_alb_tag(alb_arn)
    lb_arn = alb_arn.split(':')[-1]
    lb_arn = lb_arn.replace('loadbalancer/', '')
    alb_name = lb_arn.split('/')[1]
    if get_target_arn(alb_arn):
        tg_arn = get_target_arn(alb_arn)
        tg_name = tg_arn.split('/')[1]
        lb_info = {'alb_arn': lb_arn, "alb_name": alb_name, 'tg_arn': tg_arn,
                   "tg_name": tg_name, "tag": tag, "scheme": scheme}
        return lb_info
    lb_info = {'alb_arn': alb_arn, 'alb_name': alb_name, "tag": tag, "scheme": scheme}
    return lb_info


def get_alb_tag(alb_arn):
    """Get Alb Tags"""
    response = alb_client.describe_tags(ResourceArns=[alb_arn])
    tags = response['TagDescriptions'][0]['Tags']
    if tags:
        for tag in tags:
            if tag['Key'] == "billing_unit":
                value = tag['Value']
                if value in alias_dict:
                    return alias_dict[value]
    return "NA"


# Getting ELB Info

def get_elb_tag(elb_name):
    """Get ELB name"""
    response = elb_client.describe_tags(LoadBalancerNames=[elb_name])
    tags = response['TagDescriptions'][0]['Tags']
    if tags:
        for tag in tags:
            if tag['Key'] == "billing_unit":
                value = tag['Value']
                return alias_dict[value]
    return "NA"


def get_elb_info(elb):
    """Get ELB Info"""
    response = elb_client.describe_load_balancers(LoadBalancerNames=[elb])
    info = response['LoadBalancerDescriptions'][0]
    scheme = info['Scheme']
    tag = get_elb_tag(elb)
    elb_info = {'scheme': scheme, 'tag': tag}
    return elb_info


def put_elb_latency(alarm_name, elb_name, sns_arn):
    """Put ELB Latency Alarm"""
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
    """Put ELB 5XX Alarm"""
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
    """Put ELB Backend 5XX Alarm"""
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
    """Put ELB Unhealthy Alarm"""
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


def put_4xx_alb_alarm(name, tg_arn, alb_arn, sns_arn):
    """Put ALB 4XX Alarm"""
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
    """Put ALB 5XX Alarm for TG"""
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


def put_5xx_alb_alarm(name, alb_arn, sns_arn):
    """Put ALB 5XX Alarm"""
    alarm_name = f'{name}:HTTPCode_ELB_5XX_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='HTTPCode_ELB_5XX_Count',
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
        ])
    return response


def put_target_resp_alb_alarm(name, alb_arn, tg_arn, sns_arn):
    """Put ALB target response time alarm"""
    alarm_name = f'{name}:TargetResponseTime'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='TargetResponseTime',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Average',
        Threshold=5,
        AlarmDescription='ALB TargetResponse Alarm',
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


def put_alb_unhealthyhost(name, alb_arn, tg_arn, sns_arn):
    """Put ALB Unhealthy host alarm"""
    alarm_name = f'{name}:UnHealthyHostCount'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='UnHealthyHostCount',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Average',
        Threshold=1,
        AlarmDescription='ALB UnHealthy Host Count',
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


# GET LB NAME for type as elb or alb

def get_alarm_names(lb_name, lb_type):
    """Get ALB Alarms"""
    cw_client = boto3.client('cloudwatch')
    alarms = []
    names = []
    response = cw_client.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw_client.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
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


# SNS

def pub_sns(arn, msg, sub):
    """function for pushing msg to SNS"""
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return response


def lambda_handler(event, context):
    """Lambda Handler Function"""
    print("sleeping for 3 min")
    cw_client = boto3.client('cloudwatch')
    print(json.dumps(event))
    message = event["detail"]
    # USERNAME
    username = "NA"
    user_identity = event["detail"]["user_identity"]
    if user_identity['type'] == "IAMUser":
        username = user_identity["userName"]
    elif user_identity['type'] == "AssumedRole":
        username = user_identity["sessionContext"]["sessionIssuer"]["userName"]
    acct = event["account"]
    region = event["region"]
    print(username)

    if message["eventName"] == "CreateLoadBalancer":
        if "type" in message["requestParameters"]:
            print("CREATING ALB ALARMS")
            lb_details = message["responseElements"]['loadBalancers'][0]
            alb_arn_raw = lb_details["loadBalancerArn"]
            print("ALB ARN: ", alb_arn_raw)
            alb_info = get_alb_info(alb_arn_raw)
            print(alb_info)
            tag = alb_info['tag']
            alb_name = alb_info['alb_name']
            alb_arn = alb_info['alb_arn']
            scheme = alb_info['scheme']
            name = f'{tag}:{alb_name}:{scheme}'
            if 'tg_arn' in alb_info:
                tg_name = alb_info['tg_name']
                tg_arn = alb_info['tg_arn']
                name_with_tg = f'{tag}:{alb_name}:{tg_name}:{scheme}'
                put_alb_unhealthyhost(name_with_tg, alb_arn, tg_arn, ALERT_SNS_ARN)
                put_target_resp_alb_alarm(name_with_tg, alb_arn, tg_arn, ALERT_SNS_ARN)
                put_5xx_alb_target_alarm(name, tg_arn, alb_arn, ALERT_SNS_ARN)
                put_4xx_alb_alarm(name, tg_arn, alb_arn, ALERT_SNS_ARN)
            put_5xx_alb_alarm(name, alb_arn, ALERT_SNS_ARN)

            msg = (f'Cloudwatch Alarm Created for ALB: '
                   f'{alb_arn}\nFollowing Alarm Created:\n=============\n-5XX\n-4XX'
                   f'\n-UnHealthyHost\n-TargetResponse\n=============\nRegion: '
                   f'{region}\nAccountId: {acct}\nUse'
                   f'rName: {username}')
            sub = f'CloudWatch Alarm Created: ALB ({alb_arn})'
            print(pub_sns(SNS_ARN, msg, sub))

        else:
            lb_name = message["requestParameters"]["loadBalancerName"]
            print("CREATING ELB ALARMS")
            print(lb_name)
            elb_info = get_elb_info(lb_name)
            tag = elb_info['tag']
            scheme = elb_info['scheme']
            name = f'{tag}:{lb_name}:{scheme}'
            put_elb_unhealthy(name, lb_name, ALERT_SNS_ARN)
            put_elb_backend_5xx(name, lb_name, ALERT_SNS_ARN)
            put_elb_latency(name, lb_name, ALERT_SNS_ARN)
            put_elb_5xx(name, lb_name, ALERT_SNS_ARN)
            msg = (f'Cloudwatch Alarm Created for ELB: '
                   f'{lb_name}\nFollowing Alarm Created:\n============='
                   f'\n-5XX_Backend\n-5XX_ELB\n-UnHealthyHost\n-Latency\n'
                   f'=============\nRegion: {region}\nAccountId: '
                   f'{acct}\nUserName: {username}')
            sub = f'CloudWatch Alarm Created: ELB ({lb_name})'
            print(pub_sns(SNS_ARN, msg, sub))

    elif message["eventName"] == "DeleteLoadBalancer":
        if "loadBalancerName" in message["requestParameters"]:
            lb_name = message["requestParameters"]["loadBalancerName"]
            alarm_names = get_alarm_names(lb_name, 'elb')
            for alarm in alarm_names:
                print(f'Deleting {alarm}')
                print(cw_client.delete_alarms(AlarmNames=alarm_names))
            msg = f'Following CW Alarm has been deleted for ELB {lb_name}:\n{alarm_names}'
            sub = f'CloudWatch Alarm Deleted: {lb_name}'
            print(pub_sns(SNS_ARN, msg, sub))

        elif "loadBalancerArn" in message["requestParameters"]:
            lb_arn = message["requestParameters"]["loadBalancerArn"].split(':')[-1].replace('loadbalancer/', '')
            print(lb_arn)
            alarm_names = get_alarm_names(lb_arn, 'alb')
            for alarm in alarm_names:
                print(f'Deleting {alarm}')
                print(cw_client.delete_alarms(AlarmNames=alarm_names))
            msg = f'Following CW Alarm has been deleted for ALB {lb_arn}:\n{alarm_names}'
            sub = f'CloudWatch Alarm Deleted: {lb_arn}'
            print(pub_sns(SNS_ARN, msg, sub))
