import boto3

REGION = ""

cw = boto3.client("cloudwatch", region_name=REGION)
elb_client = boto3.client('elb', region_name=REGION)

# billing_unit: environment list
alias_dict = {'rc_production': 'RC', 'reverie_production': 'Reverie'}

ALERT_SNS_ARN = ""

lb_name = ""


def get_elb_tag(elb_name):
    response = elb_client.describe_tags(LoadBalancerNames=[elb_name])
    tags = response['TagDescriptions'][0]['Tags']
    if len(tags) == 0:
        return "NA"
    else:
        for tag in tags:
            if tag['Key'] == "billing_unit":
                value = tag['Value']
                return alias_dict[value]
    return "NA"


def get_elb_info(elb):
    response = elb_client.describe_load_balancers(LoadBalancerNames=[elb])
    info = response['LoadBalancerDescriptions'][0]
    scheme = info['Scheme']
    tag = get_elb_tag(elb)
    elb_info = {'scheme': scheme, 'tag': tag}
    return elb_info


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


print("CREATING ELB ALARMS")
print(lb_name)
elb_info = get_elb_info(lb_name)
tag = elb_info['tag']
scheme = elb_info['scheme']
name = f'{tag}:{lb_name}:{scheme}'
put_elb_unhealthy(name, lb_name, ALERT_SNS_ARN)
put_elb_backend_5xx(name, lb_name, ALERT_SNS_ARN)
put_elb_latency(name, lb_name, ALERT_SNS_ARN)
put_elb_5xx(name, lb_name, ALERT_SNS_ARN)
