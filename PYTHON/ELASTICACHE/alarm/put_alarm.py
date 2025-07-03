import boto3

SNS_ARN = "arn:aws:REDACTED"
cw = boto3.client('cloudwatch')
ecs = boto3.client('elasticache')

ACCOUNT_ID = "272110293415"
REGION = "ap-southeast-1"


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


def put_cpu_alarm(cluster_id, node, env, name):
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


def put_eviction_alarm(cluster_id, node, env, name):
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


def put_swap_alarm(cluster_id, node, env, name):
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


def put_curr_conn_alarm(cluster_id, node, env, name):
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


def put_rep_lag_alarm(cluster_id, node, env, name):
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


def put_freeable_mem_alarm(cluster_id, node, env, name):
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


def put_engine_cpu_alarm(cluster_id, node, env, name):
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


cache_clusters_info = ecs.describe_cache_clusters()['CacheClusters']

for item in cache_clusters_info:
    cache_cluster_id = item['CacheClusterId']
    cache_arn = f'arn:aws:REDACTED'
    env = get_bill_tag(cache_arn)
    name = get_name_tag(cache_arn)
    print(cache_cluster_id, cache_arn, env, name)
    # put_cpu_alarm(cache_cluster_id, env, name)
    # put_curr_conn_alarm(cache_cluster_id, env, name)
    # put_engine_cpu_alarm(cache_cluster_id, env, name)
    # put_eviction_alarm(cache_cluster_id, env, name)
    # put_freeable_mem_alarm(cache_cluster_id, env, name)
    # put_rep_lag_alarm(cache_cluster_id, env, name)
    # put_swap_alarm(cache_cluster_id, env, name)

for item in cache_clusters_info:
    cache_cluster_id = item['CacheClusterId']
    cache_arn = f'arn:aws:REDACTED'
    if item['Engine'] == "redis":
        if 'ReplicationGroupId' in item:
            cluster_name = item['ReplicationGroupId']
            env = get_bill_tag(cache_arn)
            name = get_name_tag(cache_arn)
            print(cluster_name, cache_cluster_id, cache_arn, env, name)
        else:
            


            




