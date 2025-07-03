import boto3

cw = boto3.client('cloudwatch', region_name="ap-south-1")

SNS_ARN = "arn:aws:REDACTED"
LAMBDA_ARN = "arn:aws:REDACTED"


def get_alb_alarm_names():
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if "MetricName" in alarm:
            if alarm['MetricName'] == "UnHealthyHostCount" and alarm["Namespace"] == 'AWS/ApplicationELB':
                name = alarm['AlarmName']
                tg_arn = alarm['Dimensions'][1]["Value"]
                lb_arn = alarm['Dimensions'][0]["Value"]
                print(f'Name: {name}\ntg_arn: {tg_arn}\nlb_arn: {lb_arn}')
                print(put_alb_unhealthy(name, lb_arn, tg_arn, SNS_ARN, LAMBDA_ARN),"\n\n")


def get_elb_alarm_names():
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if "MetricName" in alarm:
            if alarm['MetricName'] == "UnHealthyHostCount" and alarm["Namespace"] == 'AWS/ELB':
                elb_name = alarm['Dimensions'][0]["Value"]
                name = alarm['AlarmName']
                print(f'name: {name}\nelb_name: {elb_name}')
                print(put_elb_unhealthy(name, elb_name, SNS_ARN, LAMBDA_ARN),"\n\n")


def put_elb_unhealthy(alarm_name, elb_name, sns_arn, lambda_arn):
    alarm_name = f'{alarm_name}'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn, lambda_arn],
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


def put_alb_unhealthy(name, alb_arn, tg_arn, sns_arn, lambda_arn):
    alarm_name = f'{name}'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn, lambda_arn],
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


get_alb_alarm_names()
get_elb_alarm_names()
