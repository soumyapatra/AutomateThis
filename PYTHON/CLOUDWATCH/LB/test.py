import boto3

cw = boto3.client('cloudwatch')


def put_4xx_alb_alarm(env, alb_name, alb_arn, alb_id, sns_arn):
    alarm_name = f'{env}_{alb_name}_{alb_id}_4xx'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='HTTPCode_Target_4XX_Count',
        Namespace='AWS/ApplicationELB',
        Period=60,
        Statistic='Sum',
        Threshold=4,
        AlarmDescription='ALB 4XX Alarm',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': alb_arn
            },
        ])
    return response


put_4xx_alb_alarm('stage', 'fmscash-stage-pt-alb',
                  'arn:aws:REDACTED',
                  '8485369463487597', 'arn:aws:REDACTED')
