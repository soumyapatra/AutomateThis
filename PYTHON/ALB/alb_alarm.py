"""
Script for Putting ALB Alarms
"""
import boto3

cw = boto3.client('cloudwatch')


def put_4xx_alb_alarm(name, env, sns_arn, alb_arn):
    """Put Alb 4XX Alarm"""
    alarm_name = f'{env}_{name}_4xx'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='HTTPCode_Target_4XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Sum',
        Threshold=1,
        AlarmDescription='ALB 4XX Alarm',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_arn
            },
        ])
    return response


def put_5xx_alb_alarm(name, env, sns_arn, alb_arn):
    """Put ALB 5XX Alarms"""
    alarm_name = f'{env}_{name}_5xx'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='HTTPCode_Target_5XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Sum',
        Threshold=1,
        AlarmDescription='ALB 5XX Alarm',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_arn
            },
        ])
    return response


def put_alb_unhealthyhost(name, env, sns_arn, alb_arn, tg_arn):
    """Put ALB Unhealthyhost alarm"""
    alarm_name = f'{env}_{name}_{alb_arn}_UnHealthyHostCount'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='UnHealthyHostCount',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Average',
        Threshold=0,
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


def put_target_resp_alb_alarm(env, sns_arn, alb_arn, tg_arn):
    """Put ALB TG response Alarm"""
    alarm_name = f'{env}_{alb_arn}_ALB_TargetResponse'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
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
