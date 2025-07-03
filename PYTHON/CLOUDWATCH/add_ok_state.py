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
            elif alarm['Namespace'] == "AWS/ELB" and alarm['MetricName'] == "HTTPCode_Backend_5XX":
                alarm_sns = alarm['AlarmActions']
                threshold = alarm['Threshold']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancerName":
                        print(name, dimension['Value'], alarm_sns, OK_SNS, threshold)
                    # put_elb_backend_5xx(name, dimension['Value'], alarm_sns, OK_SNS, threshold)
            elif alarm['Namespace'] == "AWS/ELB" and alarm['MetricName'] == "HTTPCode_ELB_5XX":
                alarm_sns = alarm['AlarmActions']
                threshold = alarm['Threshold']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancerName":
                        print(name, dimension['Value'], alarm_sns, OK_SNS, threshold)
                    # put_elb_5xx(name, dimension['Value'], alarm_sns, OK_SNS, threshold)
            elif alarm['Namespace'] == "AWS/ApplicationELB" and alarm['MetricName'] == "UnHealthyHostCount":
                threshold = alarm['Threshold']
                alarm_sns = alarm['AlarmActions']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancer":
                        alb_arn = dimension['Value']
                    if dimension['Name'] == "TargetGroup":
                        tg_arn = dimension['Value']
                print(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)
                put_alb_unhealthyhost(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)
            elif alarm['Namespace'] == "AWS/ApplicationELB" and alarm['MetricName'] == "TargetResponseTime":
                threshold = alarm['Threshold']
                alarm_sns = alarm['AlarmActions']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancer":
                        alb_arn = dimension['Value']
                    if dimension['Name'] == "TargetGroup":
                        tg_arn = dimension['Value']
                print(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)
                put_target_resp_alb_alarm(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)
            elif alarm['Namespace'] == "AWS/ApplicationELB" and alarm['MetricName'] == "HTTPCode_ELB_5XX_Count":
                threshold = alarm['Threshold']
                alarm_sns = alarm['AlarmActions']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancer":
                        alb_arn = dimension['Value']
                print(name, alb_arn, alarm_sns, OK_SNS, threshold)
                put_5xx_alb_alarm(name, alb_arn, alarm_sns, OK_SNS, threshold)
            elif alarm['Namespace'] == "AWS/ApplicationELB" and alarm['MetricName'] == "HTTPCode_Target_5XX_Count":
                threshold = alarm['Threshold']
                alarm_sns = alarm['AlarmActions']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancer":
                        alb_arn = dimension['Value']
                    if dimension['Name'] == "TargetGroup":
                        tg_arn = dimension['Value']
                print(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)
                # put_5xx_alb_target_alarm(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)
            elif alarm['Namespace'] == "AWS/ApplicationELB" and alarm['MetricName'] == "HTTPCode_Target_4XX_Count":
                threshold = alarm['Threshold']
                alarm_sns = alarm['AlarmActions']
                for dimension in alarm['Dimensions']:
                    if dimension['Name'] == "LoadBalancer":
                        alb_arn = dimension['Value']
                    if dimension['Name'] == "TargetGroup":
                        tg_arn = dimension['Value']
                print(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)
                put_4xx_alb_alarm(name, alb_arn, tg_arn, alarm_sns, OK_SNS, threshold)


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


def put_elb_5xx(alarm_name, elb_name, sns_arn, ok_sns, threshold):
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        OKActions=[ok_sns],
        AlarmActions=sns_arn,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        TreatMissingData='notBreaching',
        MetricName='HTTPCode_ELB_5XX',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Minimum',
        Threshold=threshold,
        AlarmDescription='ELB 5xx',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_elb_backend_5xx(alarm_name, elb_name, sns_arn, ok_sns, threshold):
    alarm_name = f'{alarm_name}:HTTPCode_Backend_5XX'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=sns_arn,
        OKActions=[ok_sns],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        TreatMissingData='notBreaching',
        MetricName='HTTPCode_Backend_5XX',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Minimum',
        Threshold=threshold,
        AlarmDescription='ELB Backend 5xx',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_alb_unhealthyhost(name, alb_arn, tg_arn, sns_arn, ok_sns, threshold):
    response = cw.put_metric_alarm(
        AlarmName=name,
        OKActions=[ok_sns],
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='UnHealthyHostCount',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Average',
        Threshold=threshold,
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


def put_target_resp_alb_alarm(name, alb_arn, tg_arn, sns_arn, ok_sns, threshold):
    response = cw.put_metric_alarm(
        AlarmName=name,
        OKActions=[ok_sns],
        AlarmActions=sns_arn,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='TargetResponseTime',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Average',
        Threshold=threshold,
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


def put_5xx_alb_alarm(name, alb_arn, sns_arn, ok_sns, threshold):
    response = cw.put_metric_alarm(
        AlarmName=name,
        OKActions=[ok_sns],
        AlarmActions=sns_arn,
        TreatMissingData='notBreaching',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='HTTPCode_ELB_5XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Minimum',
        Threshold=threshold,
        AlarmDescription='ALB 5XX Alarm',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_arn
            },
        ])
    return response


def put_5xx_alb_target_alarm(name, alb_arn, tg_arn, sns_arn, ok_sns, threshold):
    response = cw.put_metric_alarm(
        AlarmName=name,
        OKActions=[ok_sns],
        AlarmActions=sns_arn,
        TreatMissingData='notBreaching',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='HTTPCode_Target_5XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Minimum',
        Threshold=threshold,
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


def put_4xx_alb_alarm(name, alb_arn, tg_arn, sns_arn, ok_sns, threshold):
    response = cw.put_metric_alarm(
        AlarmName=name,
        OKActions=[ok_sns],
        AlarmActions=sns_arn,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        TreatMissingData='notBreaching',
        MetricName='HTTPCode_Target_4XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Minimum',
        Threshold=threshold,
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




get_alarm_inst(REGION)
