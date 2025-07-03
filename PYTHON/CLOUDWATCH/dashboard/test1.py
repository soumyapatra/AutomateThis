import boto3
import json
from botocore.exceptions import ClientError
import os

# This script only works for AWS integrate metrics
# Please Enter Metric NAME for Instance. Please find Below URL for Metrics Name.
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html#ec2-cloudwatch-metrics
Metrics = ['CPUUtilization', 'NetworkIn', 'NetworkOut', 'MemoryUtilization']
# Please Enter path for files
path = 'files path'
x = len(Metrics)
REGION = "ap-south-1"
DASHBOARD_NAME = "KAFKA_NEW"
REGEX_LIST = ["kafka"]
inst_no_mem = []


def list_inst_4rm_metric(region):
    cw = boto3.client('cloudwatch', region_name=region)
    response = cw.list_metrics(Namespace="CWAgent", MetricName="mem_used_percent", RecentlyActive='PT3H')
    metrics = response["Metrics"]
    inst_list = []
    for metric in metrics:
        for item in metric["Dimensions"]:
            if item["Name"] == "InstanceId":
                inst_list.append(item["Value"])
    return inst_list


def list_inst_4rm_metric_new(region, namespace, metricname):
    cw = boto3.client('cloudwatch', region_name=region)
    response = cw.list_metrics(Namespace=namespace, MetricName=metricname, RecentlyActive='PT3H')
    metrics = response["Metrics"]
    inst_list = []
    for metric in metrics:
        for item in metric["Dimensions"]:
            if item["Name"] == "InstanceId":
                inst_list.append(item["Value"])
    return inst_list


def get_instance_id(region, tag_key, reg_list):
    ec2 = boto3.client('ec2', region_name=region)
    resp = []
    inst_ids = []
    response = ec2.describe_instances(Filters=[{'Name': 'tag-key', 'Values': [tag_key]}])
    resp.extend(response["Reservations"])
    while "NextToken" in response:
        response = ec2.describe_instances(Filters=[{'Name': 'tag-key', 'Values': [tag_key]}],
                                          NextToken=response["NextToken"])
        resp.extend(response["Reservations"])
    for i in resp:
        for reg in reg_list:
            for tag in i["Instances"][0]["Tags"]:
                if tag["Key"] == tag_key and reg in tag["Value"]:
                    inst_ids.append(i["Instances"][0]["InstanceId"])
    return inst_ids


# creating template for widgets x number of times
def Wid_Append(data, region):
    data = []
    for i in range(x):
        data.append({
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 5,
            "properties": {
                "metrics": [],
                "period": 300,
                "region": region
            }
        })
    return data


def files():
    filename = []
    for r, d, f in os.walk(path):
        for files in f:  # listing files with above given path
            inst_append(files)


def inst_append(files):
    with open(path + "/" + files, encoding='utf-8') as f:  # reading files
        instance_list = f.read().splitlines()
        data_list = []
        data = Wid_Append(data_list, REGION)
        count = -1
        for metric in Metrics:
            count = count + 1
            for instance in instance_list:
                if metric == 'MemoryUtilization':
                    prop = data[count]["properties"]
                    prop['metrics'].append(list(['Linux/Memory', metric, 'InstanceId', instance]))
                    prop.update({"stat": "Average", "title": metric})
                elif metric == Metrics[count]:  # comparing metric name (count will be integer value)
                    prop = data[count]["properties"]
                    prop['metrics'].append(list(['AWS/EC2', metric, 'InstanceId', instance]))
                    prop.update({"stat": "Average", "title": metric})
    dashboard(data, files)


def inst_append_new(instances, dash_name):
    data_list = []
    data = Wid_Append(data_list, REGION)
    count = -1
    cwagent_inst_ids = list_inst_4rm_metric_new(REGION, 'CWAgent', 'mem_used_percent')
    mem_inst_ids = list_inst_4rm_metric_new(REGION, 'Linux/Memory', 'MemoryUtilization')
    for metric in Metrics:
        count = count + 1
        for instance in instances:
            if metric == 'MemoryUtilization':
                if instance in mem_inst_ids:
                    prop = data[count]["properties"]
                    prop['metrics'].append(list(['Linux/Memory', metric, 'InstanceId', instance]))
                    prop.update({"stat": "Average", "title": metric})
                elif instance in cwagent_inst_ids:
                    prop = data[count]["properties"]
                    prop['metrics'].append(list(['CWAgent', "mem_used_percent", 'InstanceId', instance]))
                    prop.update({"stat": "Average", "title": "mem_used_percent"})
                else:
                    inst_no_mem.append(instance)
                    continue
            elif metric == Metrics[count]:  # comparing metric name (count will be integer value)
                prop = data[count]["properties"]
                prop['metrics'].append(list(['AWS/EC2', metric, 'InstanceId', instance]))
                prop.update({"stat": "Average", "title": metric})
    dashboard_new(data, dash_name, REGION)


def dashboard(data, files):
    # Creating Final Json for CW Dashboard and API called to create Dasboard Per ELB
    d = dict({"widgets": data})
    json_d = json.dumps(d)
    try:
        client = boto3.client('cloudwatch')
        response = client.put_dashboard(
            DashboardName=files,
            DashboardBody=(json_d)
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterValue':  # checking dashobard name
            print(e.response['Error']['Message'])
        if e.response['Error']['Code'] == 'InvalidParameterInput':  # checking dashobard Body json format
            print(e.response['Error']['Message'])


def dashboard_new(data, name, region):
    # Creating Final Json for CW Dashboard and API called to create Dasboard Per ELB
    d = dict({"widgets": data})
    json_d = json.dumps(d)
    try:
        client = boto3.client('cloudwatch', region_name=region)
        response = client.put_dashboard(
            DashboardName=name,
            DashboardBody=json_d
        )
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterValue':  # checking dashobard name
            print(e.response['Error']['Message'])
        if e.response['Error']['Code'] == 'InvalidParameterInput':  # checking dashobard Body json format
            print(e.response['Error']['Message'])


# files()
inst_ids = get_instance_id(REGION, "Application", REGEX_LIST)

inst_append_new(inst_ids, DASHBOARD_NAME)
print(inst_no_mem)
