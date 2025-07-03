import boto3

REGION = "ap-southeast-1"
SNS_ARN = "arn:aws:REDACTED"

cw = boto3.client("cloudwatch", region_name=REGION)


def put_desired_alarm(asg_name, sns_arn, count):
    alarm_name = f'{asg_name}:DesiredTargets'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='LessThanThreshold',
        EvaluationPeriods=1,
        MetricName='GroupDesiredCapacity',
        Namespace='AWS/AutoScaling',
        Period=60,
        Statistic='Average',
        Threshold=count,
        AlarmDescription=f'{asg_name} Desired Capacity is Less than Expected Capacity({count})',
        Dimensions=[
            {
                'Name': 'AutoScalingGroupName',
                'Value': asg_name
            }
        ])
    return response


def lambda_handler(event, context):
    action = event["action"]
    asg_list = event["asg_details"]
    if action == "add":
        for asg in asg_list:
            put_desired_alarm(asg["name"], SNS_ARN, int(asg["capacity"]))
    if action == "remove":
        for asg in asg_list:
            name = asg["name"]
            alarm_name = f"{name}:DesiredTargets"
            print(cw.delete_alarms(AlarmNames=[alarm_name]))
