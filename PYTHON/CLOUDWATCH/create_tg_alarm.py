import boto3
import sys

cw = boto3.client('cloudwatch', region_name="ap-southeast-1")


def put_4xx_alb_target_alarm(name, alb_arn, tg_arn, sns_arn):
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


def put_5xx_alb_target_alarm(name, alb_arn, tg_arn, sns_arn):
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


if len(sys.argv) != 5:
    print("Need arg as <name> <tg_arn> <alb_arn> <sns_arn>")
    exit()
else:
    name = sys.argv[1]
    tg_arn = sys.argv[2]
    lb_arn = sys.argv[3]
    sns_arn = sys.argv[4]
    print(name, tg_arn, lb_arn, sns_arn)
    put_4xx_alb_target_alarm(name, lb_arn, tg_arn, sns_arn)
    put_5xx_alb_target_alarm(name, lb_arn, tg_arn, sns_arn)
    put_alb_unhealthyhost(name, lb_arn, tg_arn, sns_arn)
    put_target_resp_alb_alarm(name, lb_arn, tg_arn, sns_arn)
