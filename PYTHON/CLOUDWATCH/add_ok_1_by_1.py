import boto3

REGION = "ap-south-1"
OK_SNS = "arn:aws:REDACTED"

cw = boto3.client('cloudwatch')


def get_alarm_inst(region):
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        name = alarm['AlarmName']
        if "Namespace" in alarm:
            if alarm['Namespace'] == "AWS/ELB" and alarm['MetricName'] == "UnHealthyHostCount":
                alarm_sns = alarm['AlarmActions']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancerName":
                        threshold = alarm['Threshold']
                        print(name, dimension['Value'], alarm_sns, OK_SNS, threshold)
                # put_elb_unhealthy(name, dimension['Value'], alarm_sns, OK_SNS, threshold)


def put_elb_unhealthy(alarm_name, elb_name, sns_arn, ok_sns, threshold):
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        OKActions=[ok_sns],
        AlarmActions=sns_arn,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='UnHealthyHostCount',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Average',
        Threshold=threshold,
        AlarmDescription='ELB UnHealthyHost',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


get_alarm_inst(REGION)
