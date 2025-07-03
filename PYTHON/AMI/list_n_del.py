import re
import subprocess
import time
import traceback
from datetime import datetime
from difflib import SequenceMatcher

import boto3
import dateparser
from fuzzywuzzy import process

region = 'ap-southeast-1'
ami_client = boto3.client('ec2', region_name=region)
error_filename = './error.txt'


def upload_to_s3(filename, bucket_name, key):
    s3 = boto3.client('s3')
    s3.upload_file(filename, bucket_name, key)


def log_error(err):
    f = open(error_filename, 'a+')
    f.write(err)
    f.close()


def dereg_img(ami_id):
    ec2 = boto3.client('ec2')
    response = ec2.deregister_image(ImageId=ami_id)
    return response


def del_snp(snapshot_id):
    ec2 = boto3.client('ec2')
    response = ec2.delete_snapshot(SnapshotId=snapshot_id)
    return response


def get_snap_id(ami_id):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_images(ImageIds=[ami_id])
        snap_id = []
        for device in response['Images'][0]['BlockDeviceMappings']:
            if "Ebs" not in device:
                print("Ebs may be ephemeral")
                return None
            elif device['Ebs']['Encrypted'] == "True":
                print("Encrypted Snapshot")
                return None
            else:
                snap_id.append(device['Ebs']['SnapshotId'])
        return snap_id
    except:
        error = traceback.format_exc()
        log_error(error)
        print(f'Check log file {error_filename} for error')
        return None


def get_inst_ami_list(reg):
    ami_list = []
    ec2 = boto3.client('ec2', region_name=reg)
    response = ec2.describe_instances()

    for instance in response['Reservations']:
        ami_id = instance['Instances'][0]['ImageId']
        ami_name = get_ami_name(ami_id, region)
        if ami_name not in ami_list:
            ami_list.append(ami_name)
    return ami_list


def get_ami_name(ami_id, reg):
    ec2 = boto3.client('ec2', region_name=reg)
    response = ec2.describe_images(ImageIds=[ami_id])
    for element in response['Images']:
        return element['Name']


def sortbydate(val):
    return datetime.strptime(val[2], '%d %b %Y')


def sort_ami_by_date(ami_list, date_dict):
    sort_ami_list = []
    for ami in ami_list:
        ami_name = ami[0]
        ami += (date_dict[ami_name],)
        sort_ami_list.append(ami)
        sort_ami_list.sort(key=sortbydate)
    return sort_ami_list


def list_slice(list1):
    if len(list1) > 3:
        sliced_list = list1[: len(list1) - 3]
        return sliced_list
    else:
        return []


def ratio_match(pat, mat):
    ratio = SequenceMatcher(None, pat, mat).ratio()
    if ratio > 0.5:
        return True


response = ami_client.describe_images(Owners=['self'])

ami_dict = dict()
ami_names = []
ami_date_dict = dict()
pattern_name_length_dict = dict()
pattern_ami_name_dict = dict()
file_path = './ami_del_info.txt'
snap_count = 0

# ami_list =[]
for ami in response['Images']:
    ami_dict[ami['Name']] = ami['ImageId']
    parsed_date = dateparser.parse(ami['CreationDate'])
    date = datetime.strftime(parsed_date, '%d %b %Y')
    ami_date_dict[ami['Name']] = date
    ami_names.append(ami['Name'])

total_ami = len(ami_names)
# ami_list.append(tuple([ami['ImageId'],ami['Name'],ami['CreationDate']]))
total_ami_delete = 0
# print(ami_date_dict)
inst_ami_list = get_inst_ami_list(region)
pattern_list = []
for ami_name in ami_names:
    pattern_length = len(ami_name)
    regex1 = '_\d{10,13}$'
    regex2 = '-\d{10,13}$'
    match1 = re.search(regex1, ami_name)
    match2 = re.search(regex2, ami_name)
    if match1 is not None:
        pattern = re.sub(regex1, '', ami_name)
        pattern_name_length_dict[pattern] = pattern_length
        pattern_ami_name_dict[pattern] = ami_name
    elif match2 is not None:
        pattern = re.sub(regex2, '', ami_name)
        pattern_name_length_dict[pattern] = pattern_length
        pattern_ami_name_dict[pattern] = ami_name
    else:
        continue
    if pattern in pattern_list:
        continue
    pattern_list.append(pattern)

try:
    for pattern in pattern_list:
        match_list = process.extractBests(pattern, ami_names, score_cutoff=90, limit=400)
        match_list_length_filter = [i for i in match_list if len(i[0]) == pattern_name_length_dict[pattern]]
        ratio_filter = [i for i in match_list_length_filter if ratio_match(pattern, i[0])]
        match_num = len(ratio_filter)
        sorted_list = sort_ami_by_date(ratio_filter, ami_date_dict)
        del_ami_list = list_slice(sorted_list)
        final_del_ami_list = del_ami_list.copy()
        for inst_ami in inst_ami_list:
            for ami in final_del_ami_list:
                if inst_ami == ami[0]:
                    print("Found Used AMI", inst_ami)
                    final_del_ami_list.remove(ami)
        if len(del_ami_list) == 0:
            continue
        del_ami_id_list = []
        for ami in final_del_ami_list:
            ami_id = ami_dict[ami[0]]
            del_ami_id_list.append(ami_id)
        match_ratio = []
        for ami in sorted_list:
            ratio = SequenceMatcher(None, pattern, ami[0]).ratio()
            match_ratio.append(ratio)
        total_ami_delete = total_ami_delete + len(final_del_ami_list)
        f = open(file_path, "a+")
        for ami_id in del_ami_id_list:
            print(f'\n++++++++++++++WORKING ON AMI ID: {ami_id} ++++++++++++++++++++++\n')
            f.write(f'\n++++++++++++++WORKING ON AMI ID: {ami_id} ++++++++++++++++++++++\n')
            print('Getting Snapshots::\n')
            f.write('Getting Snapshots::\n')
            snap_ids = get_snap_id(ami_id)
            if snap_ids is None:
                continue
            print(f'Deregistering AMI: {ami_id}\n')
            f.write(f'Deregistering AMI: {ami_id}\n')
            # dereg_img(ami_id)
            # time.sleep(5)
            f.write(f'AMI: {ami_id}\n')
            for snap in snap_ids:
                print(f'Deleting Snapshot: {snap}\n')
                f.write(f'Deleting Snapshot: {snap}\n')
                # del_snp(snap)
                # time.sleep(2)
                snap_count += 1
                f.write(f'{snap}\n')
        f.close()
    time_stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", datetime.utcnow().utctimetuple())
    s3_key = f'stage_ami_deletion_backup/ami_deletion_details_{time_stamp}.txt'
    print("Uploading file to s3")
    upload_to_s3(file_path, 'stage.xxxxxxxxxx.sonartest', s3_key)
except:
    error = traceback.format_exc()
    log_error(error)
    print(f'Check log file {error_filename} for error')
    subprocess.call(f'mail -s "Error in Stage AMI Deletion Cron" monitoring@xxxxxxxxxx.com < {error_filename}',
                    shell=True)

print(
    f'Total AMI Found: {total_ami}\n\nTotal AMI Will Be Deleted:{total_ami_delete}\nTotal Snapshots will be deleted: {snap_count}')

