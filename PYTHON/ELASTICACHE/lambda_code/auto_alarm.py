# AWS LAMBDA code for auto creation/deletion of elasticache replication group(redis)

import boto3
import json
import os
import time

SNS_ARN = "arn:aws:REDACTED"
cw = boto3.client('cloudwatch')
ec = boto3.client('elasticache')

ACCOUNT_ID = os.environ['ACCOUNT_ID']
REGION = os.environ['REGION']


def get_elasticache_alarm_names(cluster_id):
    alarms = []
    names = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if alarm['Namespace'] == "AWS/ElastiCache":
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "CacheClusterId":
                    alarm_name = alarm['AlarmName']
                    if len(alarm_name.split(':')) > 4:
                        alarm_name_extracted = alarm_name.split(":")[-3]
                        if cluster_id == alarm_name_extracted:
                            names.append(alarm["AlarmName"])

    return names


def get_cluster_nodes(id):
    node_list = []
    response = ec.describe_replication_groups(ReplicationGroupId=id)['ReplicationGroups'][0]
    for node in response['MemberClusters']:
        node_list.append(node)
    return node_list

def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])


def get_bill_tag(arn):
    response = ec.list_tags_for_resource(ResourceName=arn)['TagList']
    for tag in response:
        if tag['Key'] == "billing_unit":
            if tag['Value'] == "rc_production":
                return "RC"
            elif tag['Value'] == "rc_reverie":
                return "Reverie"
    return "NA"


def get_cluster_status(id):
    response = ec.describe_replication_groups(ReplicationGroupId=id)['ReplicationGroups'][0]
    return response['Status']


def get_name_tag(arn):
    response = ec.list_tags_for_resource(ResourceName=arn)['TagList']
    for tag in response:
        if tag['Key'] == "Name":
            return tag['Value']
    return "NA"


def get_cache_arn(cache_id, region, account_id):
    return f'arn:aws:REDACTED'


def put_cpu_alarm(cluster_id, node , env, name):
    alarm_name = f'{env}:{name}:{cluster_id}:{node}:CPUUtilization'
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
                'Value': node
            },
        ])
    return response


def put_eviction_alarm(cluster_id, node , env, name):
    alarm_name = f'{env}:{name}:{cluster_id}:{node}:Evictions'
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
                'Value': node
            },
        ])
    return response


def put_swap_alarm(cluster_id, node , env, name):
    alarm_name = f'{env}:{name}:{cluster_id}:{node}:SwapUsage'
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
                'Value': node
            },
        ])
    return response


def put_curr_conn_alarm(cluster_id, node , env, name):
    alarm_name = f'{env}:{name}:{cluster_id}:{node}:CurrConnections'
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
                'Value': node
            },
        ])
    return response


def put_rep_lag_alarm(cluster_id, node , env, name):
    alarm_name = f'{env}:{name}:{cluster_id}:{node}:ReplicationLag'
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
                'Value': node
            },
        ])
    return response


def put_freeable_mem_alarm(cluster_id, node , env, name):
    alarm_name = f'{env}:{name}:{cluster_id}:{node}:FreeableMemory'
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
                'Value': node
            },
        ])
    return response


def put_engine_cpu_alarm(cluster_id, node , env, name):
    alarm_name = f'{env}:{name}:{cluster_id}:{node}:EngineCPUUtilization'
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
                'Value': node
            },
        ])
    return response


def lambda_handler(event, context):
    print(json.dumps(event))
    time.sleep(240)
    event_name = event['detail']['eventName']
    if event['detail']['responseElements'] is None:
        print("Ignoring Null response")
        return
    if event_name == "CreateReplicationGroup":
        cache_cluster_id = event['detail']['responseElements']['replicationGroupId']
        status = get_cluster_status(cache_cluster_id)
        print(f'Replication group Status: {status}')
        while status != 'available':
            print(f'Replication Group {cache_cluster_id} is still in status: {status}. Waiting')
            time.sleep(5)
            status = get_cluster_status(cache_cluster_id)
        nodes = get_cluster_nodes(cache_cluster_id)
        for node in nodes:
            cache_arn = f'arn:aws:REDACTED'
            #print(f'Node ARN: {cache_arn}')
            env = get_bill_tag(cache_arn)
            name = get_name_tag(cache_arn)
            print(cache_cluster_id, node, env, name)
            put_cpu_alarm(cache_cluster_id, node, env, name)
            put_curr_conn_alarm(cache_cluster_id, node, env, name)
            put_engine_cpu_alarm(cache_cluster_id, node, env, name)
            put_eviction_alarm(cache_cluster_id, node, env, name)
            put_freeable_mem_alarm(cache_cluster_id, node, env, name)
            put_rep_lag_alarm(cache_cluster_id, node, env, name)
            put_swap_alarm(cache_cluster_id, node, env, name)
    elif event_name == "DeleteReplicationGroup":
        cache_id = event['detail']['responseElements']['replicationGroupId']
        alarm_names = get_elasticache_alarm_names(cache_id)
        for alarm in alarm_names:
            print(f'Deleting Alarm: {alarm}')
            del_alarm(alarm)



