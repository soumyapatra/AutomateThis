import re
from datetime import datetime
import time
import boto3
import dateparser
import os
import subprocess
import traceback
import sys
from tqdm import tqdm

if len(sys.argv) != 2:
    print("Enter region as args")
    exit()
else:
    REGION = sys.argv[1]

ami_info = []
ec2 = boto3.client('ec2', region_name=REGION)
file_path = './ami_deletion_details.txt'
alert_arn = "arn:aws:REDACTED"
env = "stage"
s3_bucket = 'stage.xxxxxxxxxx.sonartest'


def get_inst_ami_list(reg):
    ami_list = []
    response = ec2.describe_instances()
    for instance in response['Reservations']:
        ami_id = instance['Instances'][0]['ImageId']
        if ami_id not in ami_list:
            ami_list.append(ami_id)
    return ami_list

def dereg_img(ami_id):
    response = ec2.deregister_image(ImageId=ami_id)
    return response


def del_snp(snapshot_id):
    response = ec2.delete_snapshot(SnapshotId=snapshot_id)
    return response


def list_slice(list1):
    sliced_list = list1[: len(list1) - 3]
    return sliced_list


def sort_ami_by_date(ami_list):
    if len(ami_list) > 3:
        sorted_list = sorted(ami_list, key=lambda x: datetime.strptime(x['ami_date'], "%d %b %Y %H:%M:%S"))
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
    except:
        print("Cant get snapshots.")
        return False


def upload_to_s3(filename, bucket_name, key, region):
    s3 = boto3.client('s3', region_name=region)
    s3.upload_file(filename, bucket_name, key)


def get_del_ami(ami_list):
    if len(ami_list) > 3:
        print(sort_ami_by_date(ami_list))


total_del_ami = 0
total_del_snapshots = 0

try:
    response = ec2.describe_images(Owners=['self'])
    f = open(file_path, "a+")

    print("Creating AMI Dictionary")
    for ami in tqdm(response['Images']):
        parsed_date = dateparser.parse(ami['CreationDate'])
        date = datetime.strftime(parsed_date, '%d %b %Y %H:%M:%S')
        ami_dict = {"ami_name": ami['Name'], "ami_id": ami['ImageId'], "ami_date": date}
        ami_info.append(ami_dict)

    total_ami = len(ami_info)
    print("Got total AMI: ",total_ami)
    f.write(f'Total AMI: {total_ami}\n\n\n')

    pattern_list = []
    exact_names_list = dict()

    inst_ami_list = get_inst_ami_list(REGION)

    print("Creating AMI Pattern list")
    for ami in tqdm(ami_info):
        if ami['ami_id'] in inst_ami_list:
            f.write(f'Ignoring Used AMI: {ami}\n')
            ami_info.remove(ami)
            continue
        ami_name = ami['ami_name']
        ami_name_len = len(ami_name)
        # Search AMI with regex
        regex1 = '_\d{10,13}$'
        regex2 = '-\d{10,13}$'
        match1 = re.search(regex1, ami_name)
        match2 = re.search(regex2, ami_name)
        if match1 is not None:
            pattern = re.sub(regex1, '', ami_name)
            if pattern not in pattern_list:
                pattern_list.append(pattern)
                exact_names_list[pattern] = []
            exact_names_list[pattern].append(ami)
        elif match2 is not None:
            pattern = re.sub(regex2, '', ami_name)
            if pattern not in pattern_list:
                pattern_list.append(pattern)
                exact_names_list[pattern] = []
            exact_names_list[pattern].append(ami)

    # print(exact_names_list)
    print("Sorting all AMI patterns according to date")
    for patt, ami_list in tqdm(exact_names_list.items()):
        if patt == "bkp.rev_blog":
            continue
        if sort_ami_by_date(ami_list):
            f.write("\n\n\n")
            f.write(f'Pattern: {patt} \n=============\n=============\n')
            del_ami_list = sort_ami_by_date(ami_list)
            ignore_list = del_ami_list[-3:]
            f.write(f'Ignoring amis: {ignore_list}\n\n')
            del_ami_list = list_slice(del_ami_list)
            for ami in del_ami_list:
                total_del_ami += 1
                ami_id = ami['ami_id']
                ami_date = ami['ami_date']
                snap_ids = get_snap_id(ami_id)
                f.write(f'Deregistering AMI: {ami_id} with these snap_ids: {snap_ids} -- {ami_date}\n')
                #print(dereg_img(ami_id))
                time.sleep(1)
                for snap_id in snap_ids:
                    total_del_snapshots += 1
                    time.sleep(1)
                    #print(del_snp(snap_id))
    f.write(
        f'\n\nTotal AMI: {total_ami}\nTotal AMI Deleted: {total_del_ami}\nTotal Snapshots Deleted: {total_del_snapshots}')
    f.close()
    time_stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", datetime.utcnow().utctimetuple())
    s3_key = f'stage_ami_deletion_backup/{REGION}/ami_deletion_details_{time_stamp}.txt'
    upload_to_s3(file_path, s3_bucket, s3_key, REGION)
    sub = f"AMI Deletion completed for {env} - {REGION}"
    msg = f"Details uploaded to s3://{s3_bucket}/{s3_key}"
    print(f'File uploaded to S3 : s3://{s3_bucket}/{s3_key}')
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("file does not exist")

except:
    error_file_path = "./error.txt"
    error = traceback.format_exc()
    f = open(error_file_path, 'a+')
    f.write(error)
    f.close()
    sub = f"Error in AMI Delete cron for region {env} - {REGION}"
    subprocess.call(f'mail -s "Error in Stage AMI Deletion Cron" monitoring@xxxxxxxxxx.com < {file_path}', shell=True)
    if os.path.exists(error_file_path):
        os.remove(error_file_path)
    else:
        print("error file does not exist")
