from .ec2_ops import *
from .lambda_function import REGION
import boto3

cw = boto3.client('cloudwatch', region_name=REGION)
recover_arn = f'arn:aws:REDACTED'


def delCwAlarm(inst_id):
    cw = boto3.client('cloudwatch')
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    cw_name = []
    for metric in alarms:
        for dimension in metric['Dimensions']:
            name = dimension['Name']
            value = dimension['Value']
            if name == 'InstanceId' and value == inst_id:
                cw_name.append(metric['AlarmName'])
    for alarm in cw_name:
        print(f'Deleting Alarm {alarm}: ', del_alarm(alarm))


def put_cpu_alarm(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_CPU'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_CPU'
    response = cw.put_metric_alarm(
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


def put_mem_alarm(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_MEM'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_MEM'
    response = cw.put_metric_alarm(
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


def put_root_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_ROOT'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_ROOT'
    response = cw.put_metric_alarm(
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
                'Name': 'MountPath',
                'Value': '/'
            },
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
            {
                'Name': 'Filesystem',
                'Value': '/dev/xvda1'
            }
        ])
    return response


def put_home_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_HOME'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_HOME'
    response = cw.put_metric_alarm(
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
                'Name': 'MountPath',
                'Value': '/home'
            },
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
            {
                'Name': 'Filesystem',
                'Value': '/dev/xvdl'
            }
        ])
    return response


def put_opt_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_OPT'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_OPT'
    response = cw.put_metric_alarm(
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
                'Name': 'MountPath',
                'Value': '/opt'
            },
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
            {
                'Name': 'Filesystem',
                'Value': '/dev/xvdk'
            }
        ])
    return response


def put_autorecovery_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_AUTORECOVERY'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_AUTORECOVERY'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='StatusCheckFailed_System',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Minimum',
        Threshold=1.0,
        AlarmDescription='This metric auto recovers EC2 instances',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            }
        ])
    return response


def put_autorecovery_check_recover_action(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_AUTORECOVERY'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_AUTORECOVERY'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn, recover_arn],
        EvaluationPeriods=2,
        MetricName='StatusCheckFailed_System',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Minimum',
        Threshold=1.0,
        AlarmDescription='This metric auto recovers EC2 instances',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            }
        ])
    return response


def put_instance_status_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_STATUS_CHECK'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_STATUS_CHECK'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='StatusCheckFailed',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Maximum',
        Threshold=1,
        AlarmDescription='This metric auto recovers EC2 instances',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            }
        ])
    return response


def put_elb_latency(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:Latency'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='Latency',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Average',
        Threshold=0.1,
        AlarmDescription='ELB Latency',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_elb_5xx(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:HTTPCode_ELB_5XX'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        TreatMissingData='notBreaching',
        MetricName='HTTPCode_ELB_5XX',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Minimum',
        Threshold=1,
        AlarmDescription='ELB 5xx',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_elb_backend_5xx(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:HTTPCode_Backend_5XX'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        TreatMissingData='notBreaching',
        MetricName='HTTPCode_Backend_5XX',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Minimum',
        Threshold=1,
        AlarmDescription='ELB Backend 5xx',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_elb_unhealthy(alarm_name, elb_name, sns_arn):
    alarm_name = f'{alarm_name}:UnHealthyHostCount'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='UnHealthyHostCount',
        Namespace='AWS/ELB',
        Period=60,
        Statistic='Average',
        Threshold=1,
        AlarmDescription='ELB UnHealthyHost',
        Dimensions=[
            {
                'Name': 'LoadBalancerName',
                'Value': elb_name
            }
        ])
    return response


def put_4xx_alb_alarm(name, tg_arn, alb_arn, sns_arn):
    alarm_name = f'{name}:HTTPCode_Target_4XX_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        TreatMissingData='notBreaching',
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


def put_5xx_alb_target_alarm(name, tg_arn, alb_arn, sns_arn):
    alarm_name = f'{name}:HTTPCode_Target_5XX_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        TreatMissingData='notBreaching',
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
        TreatMissingData='notBreaching',
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


def put_nlb_target_reset(name, nlb_arn, sns_arn):
    alarm_name = f'{name}:TCP_Target_Reset_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='TCP_Target_Reset_Count',
        Namespace='AWS/NetworkELB',
        Period=60,
        Statistic='Sum',
        Threshold=1,
        AlarmDescription='NLB Target Reset Count',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': nlb_arn
            }
        ])
    return response


def put_nlb_client_reset(name, nlb_arn, sns_arn):
    alarm_name = f'{name}:TCP_Client_Reset_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='TCP_Client_Reset_Count',
        Namespace='AWS/NetworkELB',
        Period=60,
        Statistic='Sum',
        Threshold=1,
        AlarmDescription='NLB Client Reset Count',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': nlb_arn
            }
        ])
    return response


def put_nlb_elb_reset(name, nlb_arn, sns_arn):
    alarm_name = f'{name}:TCP_ELB_Reset_Count'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='TCP_ELB_Reset_Count',
        Namespace='AWS/NetworkELB',
        Period=60,
        Statistic='Sum',
        Threshold=1,
        AlarmDescription='NLB ELB Reset Count',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': nlb_arn
            }
        ])
    return response


def put_nlb_tls_error(name, nlb_arn, sns_arn):
    alarm_name = f'{name}:ClientTLSNegotiationErrorCount'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='ClientTLSNegotiationErrorCount',
        Namespace='AWS/NetworkELB',
        Period=60,
        Statistic='Sum',
        Threshold=1,
        AlarmDescription='NLB TLS Negotiation Error Count',
        Dimensions=[
            {
                'Name': 'LoadBalancer',
                'Value': nlb_arn
            }
        ])
    return response


def put_nlb_unhealthyhost(name, alb_arn, tg_arn, sns_arn):
    alarm_name = f'{name}:UnHealthyHostCount'
    print(alarm_name)
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='UnHealthyHostCount',
        Namespace='AWS/NetworkELB',
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
