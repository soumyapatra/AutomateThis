# Create Cloudwatch Alarm for Elasticache Redis Replication Group. Pass argument as Elasticache Redis Cluster Name

import boto3
import sys
import time

SNS_ARN = "arn:aws:REDACTED"
cw = boto3.client('cloudwatch')
ecs = boto3.client('elasticache')

ACCOUNT_ID = "272110293415"
REGION = "ap-southeast-1"


def list_rep_grp_id():
    grp_list = []
    response = ecs.describe_replication_groups()['ReplicationGroups']
    for item in response:
        grp_list.append(item['ReplicationGroupId'])
    return grp_list


def get_bill_tag(arn):
    response = ecs.list_tags_for_resource(ResourceName=arn)['TagList']
    for tag in response:
        if tag['Key'] == "billing_unit":
            if tag['Value'] == "rc_stage":
                return "STAGE"
    return "NA"


def get_name_tag(arn):
    response = ecs.list_tags_for_resource(ResourceName=arn)['TagList']
    for tag in response:
        if tag['Key'] == "cluster_name":
            return tag['Value']
    return "NA"


def get_status(id):
    response = ecs.describe_replication_groups(ReplicationGroupId=id)['ReplicationGroups'][0]
    return response['Status']


def get_cluster_nodes(id):
    node_list = []
    response = ecs.describe_replication_groups(ReplicationGroupId=id)['ReplicationGroups'][0]
    for node in response['MemberClusters']:
        node_list.append(node)
    return node_list


def put_cpu_alarm(cache_id, env, name):
    alarm_name = f'{env}:{name}:{cache_id}:CPUUtilization'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='CPUUtilization',
        Namespace='AWS/ElastiCache',
        Period=60,
        Statistic='Average',
        Threshold=80,
        AlarmDescription='Alarm when CPU rate exceeds',
        Dimensions=[
            {
                'Name': 'CacheClusterId',
                'Value': cache_id
            },
        ])
    return response


def put_eviction_alarm(cache_id, env, name):
    alarm_name = f'{env}:{name}:{cache_id}:Evictions'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='Evictions',
        Namespace='AWS/ElastiCache',
        Period=60,
        Statistic='Average',
        Threshold=1000,
        AlarmDescription='Alarm when Eviction count exceeds',
        Dimensions=[
            {
                'Name': 'CacheClusterId',
                'Value': cache_id
            },
        ])
    return response


def put_swap_alarm(cache_id, env, name):
    alarm_name = f'{env}:{name}:{cache_id}:SwapUsage'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='SwapUsage',
        Namespace='AWS/ElastiCache',
        Period=60,
        Statistic='Average',
        Threshold=52428800,
        AlarmDescription='Alarm when swap usage exceeds',
        Dimensions=[
            {
                'Name': 'CacheClusterId',
                'Value': cache_id
            },
        ])
    return response


def put_curr_conn_alarm(cache_id, env, name):
    alarm_name = f'{env}:{name}:{cache_id}:CurrConnections'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='CurrConnections',
        Namespace='AWS/ElastiCache',
        Period=60,
        Statistic='Sum',
        Threshold=2200,
        AlarmDescription='Alarm when connection count exceeds',
        Dimensions=[
            {
                'Name': 'CacheClusterId',
                'Value': cache_id
            },
        ])
    return response


def put_rep_lag_alarm(cache_id, env, name):
    alarm_name = f'{env}:{name}:{cache_id}:ReplicationLag'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='ReplicationLag',
        Namespace='AWS/ElastiCache',
        Period=60,
        Statistic='Average',
        Threshold=1,
        AlarmDescription='Alarm when replication lag exceeds',
        Dimensions=[
            {
                'Name': 'CacheClusterId',
                'Value': cache_id
            },
        ])
    return response


def put_freeable_mem_alarm(cache_id, env, name):
    alarm_name = f'{env}:{name}:{cache_id}:FreeableMemory'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='LessThanThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='FreeableMemory',
        Namespace='AWS/ElastiCache',
        Period=60,
        Statistic='Average',
        Threshold=524288000,
        AlarmDescription='Alarm when FreeableMemory Lowers',
        Dimensions=[
            {
                'Name': 'CacheClusterId',
                'Value': cache_id
            },
        ])
    return response


def put_engine_cpu_alarm(cache_id, env, name):
    alarm_name = f'{env}:{name}:{cache_id}:EngineCPUUtilization'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='EngineCPUUtilization',
        Namespace='AWS/ElastiCache',
        Period=60,
        Statistic='Average',
        Threshold=524288000,
        AlarmDescription='Alarm when EngineCPUUtilization exceeds',
        Dimensions=[
            {
                'Name': 'CacheClusterId',
                'Value': cache_id
            },
        ])
    return response


replication_grp_list = list_rep_grp_id()

if len(sys.argv) != 2:
    print("No or Mulitple Argument Passed")
else:
    replication_grp_id = sys.argv[1]
    if replication_grp_id not in replication_grp_list:
        print(f'Replication group {replication_grp_id} not available in region {REGION}')
    else:
        status = get_status(replication_grp_id)
        print(f'Replication group Status: {status}')
        while status != 'available':
            print(f'Replication Group {replication_grp_id} is still in status: {status}. Waiting')
            time.sleep(5)
            status = get_status(replication_grp_id)
        nodes = get_cluster_nodes(replication_grp_id)
        for node in nodes:
            cache_arn = f'arn:aws:REDACTED'
            print(f'Node ARN: {cache_arn}')
            env = get_bill_tag(cache_arn)
            name = get_name_tag(cache_arn)
            print(node, env, name)
            put_cpu_alarm(node, env, name)
            put_curr_conn_alarm(node, env, name)
            put_engine_cpu_alarm(node, env, name)
            put_eviction_alarm(node, env, name)
            put_freeable_mem_alarm(node, env, name)
            put_rep_lag_alarm(node, env, name)
            put_swap_alarm(node, env, name)