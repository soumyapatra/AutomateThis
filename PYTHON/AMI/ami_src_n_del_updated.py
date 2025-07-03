import re
from datetime import datetime
import time
import boto3
import dateparser
import os
import subprocess
import traceback
import sys

ami_backup = 5
time_stamp = time.strftime("%Y_%m_%dT%H_%M_%SZ", datetime.utcnow().utctimetuple())


def get_inst_ami_list():
    ami_list = []
    resp_list = []
    response = ec2.describe_instances()
    resp_list.extend(response["Reservations"])
    while "NextToken" in response:
        response = ec2.describe_instances(NextToken=response["NextToken"])
        resp_list.extend(response["Reservations"])
    for instance in resp_list:
        ami_id = instance['Instances'][0]['ImageId']
        if ami_id not in ami_list:
            ami_list.append(ami_id)
    return ami_list


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return response


def dereg_img(ami_id):
    response = ec2.deregister_image(ImageId=ami_id)
    return response


def del_snp(snapshot_id):
    response = ec2.delete_snapshot(SnapshotId=snapshot_id)
    return response


def list_slice(list1, num):
    sliced_list = list1[: len(list1) - num]
    return sliced_list


def sort_ami_by_date(list_ami, ami_req):
    if len(list_ami) > ami_req:
        sorted_list = sorted(list_ami, key=lambda x: datetime.strptime(x['ami_date'], "%d %b %Y %H:%M:%S"))
        return sorted_list
    else:
        return False


def get_snap_id(ami_id):
    try:
        response = ec2.describe_images(ImageIds=[ami_id])
        snap_id = []
        for device in response['Images'][0]['BlockDeviceMappings']:
            snap_id.append(device['Ebs']['SnapshotId'])
        return snap_id
    except Exception as e:
        print("Cant get snapshots.", e)
        return False


def upload_to_s3(filename, bucket_name, key, region):
    s3 = boto3.client('s3', region_name=region)
    s3.upload_file(filename, bucket_name, key)


def get_ami_dict():
    ami_info = []
    response = ec2.describe_images(Owners=['self'])
    for ami in response['Images']:
        parsed_date = dateparser.parse(ami['CreationDate'])
        date = datetime.strftime(parsed_date, '%d %b %Y %H:%M:%S')
        ami_dict = {"ami_name": ami['Name'], "ami_id": ami['ImageId'], "ami_date": date}
        ami_info.append(ami_dict)
    return ami_info


def get_pattern(regex, name):
    match = re.search(regex, name)
    if match is not None:
        return re.sub(regex, '', name)
    else:
        return False


def rem_inst_ami(list_ami):
    inst_ami_list = get_inst_ami_list()
    for item in list_ami:
        if item["ami_id"] in inst_ami_list:
            list_ami.remove(item)
    return list_ami


def rem_inst_ami_list(list_ami):
    ami_list = []
    inst_ami_list = get_inst_ami_list()
    for item in list_ami:
        if item["ami_id"] in inst_ami_list:
            ami_list.append(item)
    return ami_list


def get_ami_list(file_name):
    total_del_ami = 0
    total_del_snapshots = 0
    f = open(file_name, "a+")
    ami_info = get_ami_dict()
    all_ami = len(ami_info)
    f.write(f'Total AMI: {all_ami}\n\n\n')
    f.write("Ignoring Following Used AMI:\n---------\n")
    for item in rem_inst_ami_list(ami_info):
        f.write(f'      AMI: {item}\n')
    ami_info = rem_inst_ami(ami_info)
    pattern_list = []
    exact_names_list = dict()
    for ami in ami_info:
        name = ami['ami_name']
        regex_list = ['_\d{10,13}$', '-\d{10,13}$']
        for reg in regex_list:
            if get_pattern(reg, name):
                pattern = get_pattern(reg, name)
                if pattern not in pattern_list:
                    pattern_list.append(pattern)
                    exact_names_list[pattern] = []
                exact_names_list[pattern].append(ami)
    for patt, ami_list in exact_names_list.items():
        if patt == "bkp.rev_blog":
            continue
        if sort_ami_by_date(ami_list, ami_backup):
            f.write("\n\n\n")
            f.write(f'Pattern: {patt} \n=============\n=============\n')
            del_ami_list = sort_ami_by_date(ami_list, ami_backup)
            ignore_list = del_ami_list[-ami_backup:]
            del_ami_list = list_slice(del_ami_list, ami_backup)
            total_del_ami += len(del_ami_list)
            f.write(f'Ignoring recent amis: {ignore_list}\n\nFollowing AMI will be removed:\n---------------\n')
            for ami in del_ami_list:
                ami_id = ami['ami_id']
                snap_ids = get_snap_id(ami_id)
                ami_date = ami['ami_date']
                f.write(f'{ami_id} with snapshots {snap_ids}-- {ami_date}\n')
                total_del_snapshots += len(snap_ids)
    f.write(
        f"\n\n===========================\nTotal AMI that will be deleted: {total_del_ami}\nTotal Snapshot that will be deleted: {total_del_snapshots}")
    f.close()


def del_ami_list(file_name):
    f = open(file_name, "a+")
    total_del_snapshots = 0
    ami_info = get_ami_dict()
    total_ami = len(ami_info)
    f.write(f'Total AMI: {total_ami}\n\n\n')
    f.write("Ignoring Following Used AMI:\n---------\n")
    for item in rem_inst_ami_list(ami_info):
        f.write(f'      AMI: {item}\n')
    ami_info = rem_inst_ami(ami_info)
    pattern_list = []
    exact_names_list = dict()
    for ami in ami_info:
        name = ami['ami_name']
        regex_list = ['_\d{10,13}$', '-\d{10,13}$']
        for reg in regex_list:
            if get_pattern(reg, name):
                pattern = get_pattern(reg, name)
                if pattern not in pattern_list:
                    pattern_list.append(pattern)
                    exact_names_list[pattern] = []
                exact_names_list[pattern].append(ami)
    for patt, ami_list in exact_names_list.items():
        if patt == "bkp.rev_blog":
            continue
        if sort_ami_by_date(ami_list, ami_backup):
            f.write("\n\n\n")
            f.write(f'Pattern: {patt} \n=============\n=============\n')
            del_ami_list = sort_ami_by_date(ami_list, ami_backup)
            ignore_list = del_ami_list[-ami_backup:]
            del_ami_list = list_slice(del_ami_list, ami_backup)
            f.write(f'Ignoring recent amis: {ignore_list}\n\nRemoving following AMI:\n---------------\n')
            for ami in del_ami_list:
                ami_id = ami['ami_id']
                snap_ids = get_snap_id(ami_id)
                ami_date = ami['ami_date']
                f.write(f'{ami_id} with snapshots {snap_ids}-- {ami_date}\n')
                # print(dereg_img(ami_id))
                for snap_id in snap_ids:
                    total_del_snapshots += 1
                    time.sleep(1)
                    # print(del_snp(snap_id))
    f.close()


if len(sys.argv) != 3:
    print("Required Args as #script.py region report/delete")
    exit()
else:
    REGION = sys.argv[1]
    report_file_path = f'./ami_deletion_report_details_{time_stamp}_{REGION}.txt'
    ec2 = boto3.client('ec2', region_name=REGION)
    action = sys.argv[2]
    if action == "report":
        get_ami_list(report_file_path)
    elif action == "delete":
        pass
    else:
        print("Wrong arg entered. Please enter report or delete")
