import boto3

def get_trgt_arn(lb_arn):
    alb = boto3.client('elbv2')
    response = alb.describe_target_groups(
        LoadBalancerArn=lb_arn)
    return response["TargetGroups"]

print(get_trgt_arn('arn:aws:REDACTED'))
