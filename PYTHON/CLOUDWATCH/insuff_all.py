import boto3
import os

SNS_ARN=os.environ['SNS_ARN']

cw=boto3.client('cloudwatch')
ec2=boto3.resource('ec2')

def pub_sns(arn,msg,sub):
    sns=boto3.client('sns')
    response = sns.publish(
        TargetArn = arn,
        Subject= sub,
        Message = msg,
    )
    return response


def get_inst_ids():
    cw=boto3.resource('ec2')
    inst_ids=[]
    instances=ec2.instances.filter()
    for instance in instances:
        inst_ids.append(instance.id)
    return inst_ids

def get_lb():
    elb=boto3.client('elb')
    response=elb.describe_load_balancers()
    lbs=[]
    elb_names=[]
    lbs.extend(response["LoadBalancerDescriptions"])
    if 'NextMarker' in response:
        response = elb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancerDescriptions"])
    for lb in lbs:
        elb_names.append(lb["LoadBalancerName"])
    return elb_names

def get_alb():
    alb = boto3.client('elbv2')
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancers"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        alb_names.append(lb["LoadBalancerArn"].split(':')[-1].replace('loadbalancer/',''))
    return alb_names



def chk_alarm(resource_type):
    alarms = []
    insuff_alarm=[]
    response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])

    if resource_type == "instance":
        inst_ids=get_inst_ids()
        for alarm in alarms:
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "InstanceId" and dimension["Value"] not in inst_ids:
                    insuff_alarm.append(alarm['AlarmName'])
                    return insuff_alarm

    elif resource_type == "elb":
        elbs=get_lb()
        for alarm in alarms:
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "LoadBalancerName" and dimension["Value"] not in elbs:
                    insuff_alarm.append(alarm['AlarmName'])
                    return insuff_alarm
    elif resource_type == "alb":
        albs=get_alb()
        for alarm in alarms:
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "LoadBalancer" and dimension["Value"] not in albs:
                    insuff_alarm.append(alarm['AlarmName'])
                    return insuff_alarm
    else:
        return

def lambda_handler(event,handler):
    insuff_inst_alarm=chk_alarm('instance')
    insuff_elb_alarm=chk_alarm('elb')
    insuff_alb_alarm=chk_alarm('alb')

    if len(insuff_alb_alarm) == 0 and len(insuff_elb_alarm) == 0 and len(insuff_inst_alarm) == 0:
        return
    else:
        msg=f'Insufficient Alarms\n======================\nInstance: {insuff_inst_alarm}\nALB: {insuff_alb_alarm}\nELB: {insuff_elb_alarm}\n======================'
        pub_sns(SNS_ARN,msg,"Insufficient Alarms With No Resources")
        print(msg)
