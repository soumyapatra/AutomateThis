import boto3
from datetime import datetime
import csv
from botocore.exceptions import ClientError
from tqdm import tqdm
import sys
import time
from datetime import timedelta

# starttime = datetime(2020, 8, 17)
# endtime = datetime(2020, 10, 17)


time_stamp = time.strftime("%Y_%m_%dT%H_%M_%SZ", datetime.utcnow().utctimetuple())


def get_inst_tag(inst_id, tag_name, region):
    try:
        ec2 = boto3.client('ec2', region_name=region)

        response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
        tags = response['Tags']
        for tag in tags:
            if tag['Key'] == tag_name:
                return tag['Value']
        return "NA"
    except ClientError:
        print("Instance Does not exist")
        return


def get_cpu_metric(inst_id, period, region, starttime, endtime):
    file_name = f"top_cpu_{time_stamp}.csv"
    cw = boto3.client('cloudwatch', region_name=region)
    col_head = "InstanceID, InstanceName, TOP6, DATE6, TOP5, DATE5, TOP4, DATE4, TOP3, DATE3, TOP2, DATE2, TOP1, DATE1\n"
    col_write = open(file_name, "w")
    col_write.write(col_head)
    col_write.close()
    metric_list = []
    response = cw.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
        ],
        # StartTime=datetime.now() - timedelta(days=90),
        # EndTime=datetime.now(),
        StartTime=starttime,
        EndTime=endtime,
        #        Period=1382400,
        Period=period,
        Statistics=['Maximum'],
    )
    for data in response['Datapoints']:
        metric_list.append(data)

    # print(metric_list)

    def myFunc(e):
        return e['Maximum']

    metric_list.sort(key=myFunc, reverse=True)

    def get_item(index, list, key):
        if len(list) > index:
            return list[index][key]
        else:
            return "Null"

    instance_name = get_inst_tag(inst_id, "Name")
    with open(file_name, "a") as csvFile:
        # parsed_data = inst_id,instance_name,metric_list[0]['Maximum'],metric_list[0]['Timestamp'],metric_list[1]['Maximum'],metric_list[1]['Timestamp'],metric_list[2]['Maximum'],metric_list[2]['Timestamp'],metric_list[3]['Maximum'],metric_list[3]['Timestamp'], metric_list[4]['Maximum'],metric_list[4]['Timestamp'],metric_list[5]['Maximum'],metric_list[5]['Timestamp']
        parsed_data = inst_id, instance_name, get_item(0, metric_list, "Maximum"), get_item(0, metric_list,
                                                                                            "Timestamp"), get_item(
            1,
            metric_list,
            "Maximum"), get_item(
            1, metric_list, "Timestamp"), get_item(2, metric_list, "Maximum"), get_item(2, metric_list,
                                                                                        "Timestamp"), get_item(3,
                                                                                                               metric_list,
                                                                                                               "Maximum"), get_item(
            3, metric_list, "Timestamp"), get_item(4, metric_list, "Maximum"), get_item(4, metric_list,
                                                                                        "Timestamp"), get_item(5,
                                                                                                               metric_list,
                                                                                                               "Maximum"), get_item(
            5, metric_list, "Timestamp")
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(parsed_data)


def get_mem_metric_linux(inst_id):
    metric_list = []
    response = cw.get_metric_statistics(
        Namespace='Linux/Memory',
        MetricName='MemoryUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
        ],
        StartTime=starttime,
        EndTime=endtime,
        Period=period,
        Statistics=['Maximum'],
    )
    if len(response['Datapoints']) == 0:
        get_mem_metric_cwagent(inst_id)
        return

    for data in response['Datapoints']:
        metric_list.append(data)

    def myFunc(e):
        return e['Maximum']

    metric_list.sort(key=myFunc, reverse=True)

    def get_item(index, list, key):
        if len(list) > index:
            return list[index][key]
        else:
            return "Null"

    instance_name = get_inst_tag(inst_id, "Name")
    acr_tag = get_inst_tag(inst_id, "acr_reporting")
    with open(FILE, "a") as csvFile:
        # parsed_data = inst_id,instance_name,metric_list[0]['Maximum'],metric_list[0]['Timestamp'],metric_list[1]['Maximum'],metric_list[1]['Timestamp'],metric_list[2]['Maximum'],metric_list[2]['Timestamp'],metric_list[3]['Maximum'],metric_list[3]['Timestamp'], metric_list[4]['Maximum'],metric_list[4]['Timestamp'],metric_list[5]['Maximum'],metric_list[5]['Timestamp']
        parsed_data = inst_id, instance_name, get_item(0, metric_list, "Maximum"), get_item(0, metric_list,
                                                                                            "Timestamp"), get_item(
            1,
            metric_list,
            "Maximum"), get_item(
            1, metric_list, "Timestamp"), get_item(2, metric_list, "Maximum"), get_item(2, metric_list,
                                                                                        "Timestamp"), get_item(3,
                                                                                                               metric_list,
                                                                                                               "Maximum"), get_item(
            3, metric_list, "Timestamp"), get_item(4, metric_list, "Maximum"), get_item(4, metric_list,
                                                                                        "Timestamp"), get_item(5,
                                                                                                               metric_list,
                                                                                                               "Maximum"), get_item(
            5, metric_list, "Timestamp")
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(parsed_data)


def get_mem_metric_cwagent(inst_id):
    metric_list = []
    response = cw.get_metric_statistics(
        Namespace='CWAgent',
        MetricName='mem_used_percent',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
        ],
        StartTime=starttime,
        EndTime=endtime,
        Period=period,
        Statistics=['Maximum'],
    )

    for data in response['Datapoints']:
        metric_list.append(data)

    def myFunc(e):
        return e['Maximum']

    metric_list.sort(key=myFunc, reverse=True)

    def get_item(index, list, key):
        if len(list) > index:
            return list[index][key]
        else:
            return "Null"

    instance_name = get_inst_tag(inst_id, "Name")
    acr_tag = get_inst_tag(inst_id, "acr_reporting")
    with open(FILE, "a") as csvFile:
        # parsed_data = inst_id,instance_name,metric_list[0]['Maximum'],metric_list[0]['Timestamp'],metric_list[1]['Maximum'],metric_list[1]['Timestamp'],metric_list[2]['Maximum'],metric_list[2]['Timestamp'],metric_list[3]['Maximum'],metric_list[3]['Timestamp'], metric_list[4]['Maximum'],metric_list[4]['Timestamp'],metric_list[5]['Maximum'],metric_list[5]['Timestamp']
        parsed_data = inst_id, instance_name, get_item(0, metric_list, "Maximum"), get_item(0, metric_list,
                                                                                            "Timestamp"), get_item(
            1,
            metric_list,
            "Maximum"), get_item(
            1, metric_list, "Timestamp"), get_item(2, metric_list, "Maximum"), get_item(2, metric_list,
                                                                                        "Timestamp"), get_item(3,
                                                                                                               metric_list,
                                                                                                               "Maximum"), get_item(
            3, metric_list, "Timestamp"), get_item(4, metric_list, "Maximum"), get_item(4, metric_list,
                                                                                        "Timestamp"), get_item(5,
                                                                                                               metric_list,
                                                                                                               "Maximum"), get_item(
            5, metric_list, "Timestamp")
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(parsed_data)


# get_cpu_metric("i-0cb022e14f77fa34d")


def get_instance_ids(region):
    ec2 = boto3.resource('ec2', region_name=region)
    running_instances = ec2.instances.all()
    #    running_instances = ec2.instances.filter(Filters=[{
    #        'Name': 'instance-state-name',
    #        'Values': ['running']}])
    ids = []
    for instance in running_instances:
        ids.append(instance.id)
    return ids


if len(sys.argv) != 5:
    print("Required Args as #script.py region CPU/MEM/ALL time_period_in_sec days")
    exit()
else:
    REGION = sys.argv[1]
    time_period = sys.argv[3]
    no_of_days = sys.argv[4]
    if isinstance(no_of_days, int) is False:
        print("Please enter No. of Days as Number")
        exit()
    StartTime = datetime.now() - timedelta(days=no_of_days),
    EndTime = datetime.now()
    ec2 = boto3.client('ec2', region_name=REGION)
    instance_ids = get_instance_ids(REGION)
    action = sys.argv[2]
    if action == "CPU":
        for instance in tqdm(instance_ids):
            get_cpu_metric(instance, time_period, REGION, StartTime, EndTime)
    elif action == "ALL":
        for instance in tqdm(instance_ids):
            get_cpu_metric(instance, time_period)
            get_mem_metric_linux(instance)
    elif action == "MEM":
        for instance in tqdm(instance_ids):
            get_mem_metric_linux(instance)
    else:
        print("Wrong arg entered. Please enter CPU/MEM/ALL")
