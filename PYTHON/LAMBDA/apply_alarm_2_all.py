# Creating/Updating Cloudwatch Error alarm for all AWS Lambda functions in a region

import boto3

REGION = "ap-southeast-1"
cw = boto3.client('cloudwatch', region_name=REGION)
SNS_ARN = ""
lambda_client = boto3.client('lambda', region_name=REGION)
ENV = "STAGE"


def put_error_alarm(name, tag, region):
    alarm_name = f'{tag}:LAMBDA:{name}:{region}:Error'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=1,
        MetricName='Errors',
        Namespace='AWS/Lambda',
        Period=60,
        Statistic='Average',
        Threshold=1,
        AlarmDescription='Alarm when 4XX Error rate exceeds',
        Dimensions=[
            {
                'Name': 'FunctionName',
                'Value': name
            }
        ])
    return response


def get_function_names():
    lambda_details = []
    func_names = []
    response = lambda_client.list_functions(MaxItems=100)
    lambda_details.extend(response['Functions'])
    while 'NextMarker' in response:
        response = lambda_client.list_functions(MaxItems=100, Marker=response['NextMarker'])
        lambda_details.extend(response['Functions'])

    for func in lambda_details:
        func_name = func['FunctionName']
        func_names.append(func_name)
    return func_names


alarm_names = get_function_names()
for name in alarm_names:
    put_error_alarm(name, ENV, REGION)
