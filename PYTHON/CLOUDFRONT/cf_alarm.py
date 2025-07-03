import boto3

cw = boto3.client('cloudwatch', region_name='us-east-1')
cf = boto3.client('cloudfront')
SNS_ARN = "arn:aws:REDACTED"


def put_cf_tag(arn):
    response = cf.tag_resource(Resource=arn, Tags={'Items': [{'Key': 'component', 'Value': 'Infrastructure'}]})
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


def put_request_alarm(dist_id, tag, name):
    alarm_name = f'{tag}:{name}:{dist_id}:Request'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='Request',
        Namespace='AWS/CloudFront',
        Period=60,
        Statistic='Sum',
        Threshold=70.0,
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


def put_ttl_bytes_alarm(dist_id, tag, name):
    alarm_name = f'{tag}:{name}:{dist_id}:BytesDownloaded'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=2,
        MetricName='BytesDownloaded',
        Namespace='AWS/CloudFront',
        Period=60,
        Statistic='Sum',
        Threshold=70.0,
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


cf_list = cf.list_distributions()['DistributionList']['Items']
for item in cf_list:
    id_arn = item['ARN']
    id = item['Id']
    is_enabled = item['Enabled']
    tags = get_billing_tag(id_arn)
    name = get_name_tag(id_arn)
    print(id, is_enabled, id_arn, tags, name)
    print(put_4xx_alarm(id, tags, name))
    print(put_5xx_alarm(id, tags, name))
    print(put_cf_tag(id_arn))
