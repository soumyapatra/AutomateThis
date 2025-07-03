import boto3

ec2 = boto3.resource('ec2')
cw = boto3.client('cloudwatch')

def get_instance_tag(fid,tagKey):
    ec2instance = ec2.Instance(fid)
    tagVal = ""
    for tags in ec2instance.tags:
        if tags["Key"] == tagKey:
            tagVal = tags["Value"]
    return tagVal


def putcw(fid):
    cw.put_metric_alarm(
        AlarmName='CPU_Utilization_{}'.format(fid),
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmActions=[snsArn],
        AlarmDescription='Alarm when server CPU exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': fid
            },
        ],
        Unit='Seconds'
    )
    cw.put_metric_alarm(
        AlarmName='Mem_Utilization_{}'.format(fid),
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='mem_used_percent',
        Namespace='CWAgent',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmActions=[snsArn],
        AlarmDescription='Alarm when server CPU exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': fid
            },
        ],
        Unit='Seconds'
    )


instId = "i-05c70ec9034456b5b"
snsArn = "arn:aws:REDACTED"
cwStatus = get_instance_tag(instId,"cw_enabled")
if cwStatus == "yes":
    print("CW is enabled")
    putcw(instId)
