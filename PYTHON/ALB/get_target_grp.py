import boto3
import json

def get_trgt_arn(lb_arn):
    alb = boto3.client('elbv2')
    response = alb.describe_target_groups(
        LoadBalancerArn=lb_arn)
    tg_arn=response["TargetGroups"][0]["TargetGroupArn"]
    return tg_arn.split(':')[-1]
print(get_trgt_arn('arn:aws:REDACTED'))
