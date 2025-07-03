import boto3
from datetime import datetime
import json

REGION = "ap-south-1"

cw = boto3.client('cloudwatch', region_name=REGION)
ec2 = boto3.client('ec2', region_name=REGION)

ENV = 'RC'
SNS = "arn:aws:REDACTED"


def get_inst_state(id):
    ec2_client = boto3.resource('ec2')
    state = ec2_client.Instance(id).state
    return state['Name']


def get_inst_id_by_tag(tagkey, tagvalue):
    response = ec2.describe_instances(Filters=[{'Name': 'tag:' + tagkey, 'Values': [tagvalue]}])
    inst_list = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            inst_list.append(instance["InstanceId"])
    return inst_list


def get_inst_vol(id):
    response = ec2.describe_instances(InstanceIds=[id])['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
    vol_list = []
    for vol in response:
        id = vol['Ebs']['VolumeId']
        vol_list.append(id)
    return vol_list


def get_inst_tag(inst_id, tag_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
    tags = response['Tags']
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return "NA"


def put_vol_queue_len(name, id, vol_id, sns_arn, threshold_band):
    alarm_name = f'{ENV}_{name}_{id}_{vol_id}_VolumeQueueLength'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        OKActions=[sns_arn],
        EvaluationPeriods=1,
        DatapointsToAlarm=1,
        AlarmDescription="EBS Volume Queue Length Anomaly Detection",
        ComparisonOperator='LessThanLowerOrGreaterThanUpperThreshold',
        ThresholdMetricId="ad1",
        Metrics=[
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/EBS",
                        "MetricName": "VolumeQueueLength",
                        "Dimensions": [
                            {
                                "Name": "VolumeId",
                                "Value": vol_id
                            }
                        ]
                    },
                    "Period": 300,
                    "Stat": "Average"
                },
                "ReturnData": True
            },
            {
                "Id": "ad1",
                "Expression": f'ANOMALY_DETECTION_BAND(m1,{threshold_band} )',
                "Label": "VolumeQueueLength (expected)",
                "ReturnData": True
            }
        ])
    return response


def put_vol_write_latency(name, id, vol_id, sns_arn, threshold):
    alarm_name = f'{ENV}_{name}_{id}_{vol_id}_VolWriteLatency'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        OKActions=[sns_arn],
        EvaluationPeriods=1,
        DatapointsToAlarm=1,
        AlarmDescription="EBS Volume Write Latency",
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        TreatMissingData='notBreaching',
        Threshold=threshold,
        Metrics=[
            {
                "Id": "e1",
                "Expression": "m1*1000",
                "Label": "Write Latency",
                "ReturnData": True
            },
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/EBS",
                        "MetricName": "VolumeTotalWriteTime",
                        "Dimensions": [
                            {
                                "Name": "VolumeId",
                                "Value": vol_id
                            }
                        ]
                    },
                    "Period": 300,
                    "Stat": "Average"
                },
                "ReturnData": False
            }

        ])
    return response


def put_vol_read_latency(name, id, vol_id, sns_arn, threshold):
    alarm_name = f'{ENV}_{name}_{id}_{vol_id}_VolReadLatency'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmActions=[sns_arn],
        OKActions=[sns_arn],
        EvaluationPeriods=1,
        DatapointsToAlarm=1,
        AlarmDescription="EBS Volume Read Latency",
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        TreatMissingData='notBreaching',
        Threshold=threshold,
        Metrics=[
            {
                "Id": "e1",
                "Expression": "m1*1000",
                "Label": "Read Latency",
                "ReturnData": True
            },
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/EBS",
                        "MetricName": "VolumeTotalReadTime",
                        "Dimensions": [
                            {
                                "Name": "VolumeId",
                                "Value": vol_id
                            }
                        ]
                    },
                    "Period": 300,
                    "Stat": "Average"
                },
                "ReturnData": False
            }

        ])
    return response


inst_ids = get_inst_id_by_tag("Role", "database")

for id in inst_ids:
    inst_name = get_inst_tag(id, "Name")
    state = get_inst_state(id)
    if "mysql" in inst_name and state == "running":
        vol_ids = get_inst_vol(id)
        for vol in vol_ids:
            print(inst_name, id, vol, SNS)
            print(put_vol_read_latency(inst_name, id, vol, SNS, 2))
            print(put_vol_write_latency(inst_name, id, vol, SNS, 2))
            # print(put_vol_queue_len(name, vol, SNS, 2))
