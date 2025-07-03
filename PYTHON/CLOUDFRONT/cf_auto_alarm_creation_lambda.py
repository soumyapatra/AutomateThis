import boto3
import json
import os
import time

cw = boto3.client('cloudwatch', region_name="us-east-1")
cf = boto3.client('cloudfront')
SNS_ARN = os.environ['SNS']


def get_alarm_names(id):
    alarms = []
    alarm_name = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if alarm['Namespace'] == "AWS/CloudFront":
            for dimension in alarm['Dimensions']:
                if dimension['Name'] == "DistributionId" and dimension['Value'] == id:
                    alarm_name.append(alarm['AlarmName'])
    return alarm_name


def del_alarm(name):
    response = cw.delete_alarms(AlarmNames=[name])
    return response


def get_billing_tag(arn):
    response = cf.list_tags_for_resource(Resource=arn)['Tags']['Items']
    if len(response) != 0:
        for item in response:
            if item['Key'] == "billing_unit":
                if item['Value'] == "reverie_production" or item['Value'] == "production_reverie":
                    return "Reverie"
                elif item['Value'] == "rc_production":
                    return "RC"
                elif item['Value'] == "rc_stage":
                    return "STAGE"
                else:
                    return "NA"
    return "NA"


def get_name_tag(arn):
    response = cf.list_tags_for_resource(Resource=arn)['Tags']['Items']
    if len(response) != 0:
        for item in response:
            if item['Key'] == "Name":
                return item['Value']
    return "NA"


def put_4xx_alarm(dist_id, tag, name):
    alarm_name = f'{tag}:{name}:{dist_id}:4xxErrorRate'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='4xxErrorRate',
        Namespace='AWS/CloudFront',
        Period=60,
        Statistic='Average',
        Threshold=5,
        AlarmDescription='Alarm when 4XX Error rate exceeds',
        Dimensions=[
            {
                'Name': 'DistributionId',
                'Value': dist_id
            },
            {
                'Name': 'Region',
                'Value': 'Global'
            },
        ])
    return response


def put_5xx_alarm(dist_id, tag, name):
    alarm_name = f'{tag}:{name}:{dist_id}:5xxErrorRate'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='5xxErrorRate',
        Namespace='AWS/CloudFront',
        Period=60,
        Statistic='Average',
        Threshold=0.2,
        AlarmDescription='Alarm when 5XX Error rate exceeds',
        Dimensions=[
            {
                'Name': 'DistributionId',
                'Value': dist_id
            },
            {
                'Name': 'Region',
                'Value': 'Global'
            },
        ])
    return response


def lambda_handler(event, context):
    print(json.dumps(event))
    print("Sleeping for 2 min")
    time.sleep(60)
    event_details = event['detail']
    event_name = event_details['eventName']

    if event_name == "CreateDistributionWithTags":
        resp_element = event_details['responseElements']
        dist_id = resp_element['distribution']['id']
        dist_arn = resp_element['distribution']['aRN']
        print(f'Creating Clodfront Alarm for ID:{dist_id}')
        billing_tag = get_billing_tag(dist_arn)
        name_tag = get_name_tag(dist_arn)
        print(put_5xx_alarm(dist_id, billing_tag, name_tag))
        print(put_4xx_alarm(dist_id, billing_tag, name_tag))

    elif event_name == "DeleteDistribution":
        dist_id = event_details['requestParameters']['id']
        alarm_names = get_alarm_names(dist_id)
        print("Deleting Cloudfront alarm")
        for alarm in alarm_names:
            del_alarm(alarm)
