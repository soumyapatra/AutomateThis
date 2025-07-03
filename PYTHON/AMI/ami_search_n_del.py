import re
from datetime import datetime
import time
import boto3
import dateparser

ami_info = []

REGION = 'ap-south-1'
ami_client = boto3.client('ec2', region_name=REGION)

response = ami_client.describe_images(Owners=['self'])


def get_inst_ami_list(reg):
    ami_list = []
    ec2 = boto3.client('ec2', region_name=reg)
    response = ec2.describe_instances()
    for instance in response['Reservations']:
        ami_id = instance['Instances'][0]['ImageId']
        if ami_id not in ami_list:
            ami_list.append(ami_id)
    return ami_list


def dereg_img(ami_id):
    ec2 = boto3.client('ec2')
    response = ec2.deregister_image(ImageId=ami_id)
    return response


def del_snp(snapshot_id):
    ec2 = boto3.client('ec2')
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
        return


def get_snap_id(ami_id):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_images(ImageIds=[ami_id])
        snap_id = []
        for device in response['Images'][0]['BlockDeviceMappings']:
            snap_id.append(device['Ebs']['SnapshotId'])
        return snap_id
    except:
        print("Cant get snapshots.")
        return False


def get_del_ami(ami_list):
    if len(ami_list) > 3:
        print(sort_ami_by_date(ami_list))

total_del_ami = 0
total_del_snapshots = 0

for ami in response['Images']:
    parsed_date = dateparser.parse(ami['CreationDate'])
    date = datetime.strftime(parsed_date, '%d %b %Y %H:%M:%S')
    ami_dict = {"ami_name": ami['Name'], "ami_id": ami['ImageId'], "ami_date": date}
    ami_info.append(ami_dict)

total_ami = len(ami_info)
print("Total AMI's: ", total_ami)

pattern_list = []
exact_names_list = dict()

inst_ami_list = get_inst_ami_list(REGION)

for ami in ami_info:
    if ami['ami_id'] in inst_ami_list:
        print("Ignoring used AMI: ", ami)
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
for patt, ami_list in exact_names_list.items():
    if patt == "bkp.rev_blog":
        continue
    if sort_ami_by_date(ami_list):
        print("\n\n\n")
        print(f'Pattern: {patt} \n=============\n=============')
        del_ami_list = sort_ami_by_date(ami_list)
        ignore_list = del_ami_list[-3:]
        print(f'Ignoring amis: {ignore_list}/n')
        del_ami_list = list_slice(del_ami_list)
        for ami in del_ami_list:
            total_del_ami += 1
            ami_id = ami['ami_id']
            snap_ids = get_snap_id(ami_id)
            print(f'Deregistering AMI: {ami_id} with these snap_ids: {snap_ids}')
            #print(dereg_img(ami_id))
            time.sleep(1)
            for snap_id in snap_ids:
                total_del_snapshots += 1
                #print(del_snp(snap_id))

print(f'Total AMI: {total_ami}\nAMI Will be Deleted: {total_del_ami}\nTotal Snapshots: {total_del_snapshots}')
