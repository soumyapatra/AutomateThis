import boto3
import logging
import json

cw=boto3.client('cloudwatch')

inst_id='i-0898b3661cfdae430'
sns_arn="arn:aws:REDACTED"
def put_cpu_alarm(inst_id):
    alarm_name=f'{inst_id}_CPU'
    response=cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server CPU exceeds 70%',
        Dimensions=[
        {
          'Name': 'InstanceId',
          'Value': inst_id
        },
        ])
    return response

def put_mem_alarm(inst_id):
    alarm_name=f'{inst_id}_MEM'
    response=cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='MemoryUtilization',
        Namespace='Linux/Memory',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server MEMORY exceeds 70%',
        Dimensions=[
        {
          'Name': 'InstanceId',
          'Value': inst_id
        },
        ])
    return response

def put_root_check(inst_id):
    alarm_name=f'{inst_id}_ROOT'
    response=cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='DiskUtilization',
        Namespace='Linux/Disk',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server ROOT exceeds 70%',
        Dimensions=[
            {
                'Name':'MountPath',
                'Value':'/'
            },
            {
                'Name':'InstanceId',
                'Value':inst_id
            },
            {
                'Name':'Filesystem',
                'Value':'/dev/xvda1'
            }
        ])
    return response

def put_home_check(inst_id):
    alarm_name=f'{inst_id}_HOME'
    response=cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='DiskUtilization',
        Namespace='Linux/Disk',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server HOME exceeds 70%',
        Dimensions=[
            {
                'Name':'MountPath',
                'Value':'/home'
            },
            {
                'Name':'InstanceId',
                'Value':inst_id
            },
            {
                'Name':'Filesystem',
                'Value':'/dev/xvdb'
            }
        ])
    return response

def put_opt_check(inst_id):
    alarm_name=f'{inst_id}_OPT'
    response=cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='DiskUtilization',
        Namespace='Linux/Disk',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server OPT exceeds 70%',
        Dimensions=[
            {
                'Name':'MountPath',
                'Value':'/opt'
            },
            {
                'Name':'InstanceId',
                'Value':inst_id
            },
            {
                'Name':'Filesystem',
                'Value':'/dev/xvde'
            }
        ])
    return response
print(put_cpu_alarm(inst_id))
print(put_root_check(inst_id))
print(put_home_check(inst_id))
print(put_mem_alarm(inst_id))
print(put_opt_check(inst_id))

def lambda_handler(event, context):
    logging.info(json.loads(event))
