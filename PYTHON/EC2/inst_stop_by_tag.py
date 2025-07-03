import boto3
import json
from datetime import date


def get_tag_val(inst_id,tag_name):
    ec2=boto3.resource('ec2')
    instance=ec2.Instance(inst_id)
    for tag in instance.tags:
        if tag["Key"] == tag_name:
            return tag["Value"]
        else:
            return 


def get_inst_id():
    ec2=boto3.resource('ec2')
    instances=ec2.instances.filter()
    inst_list=[]
    for instance in instances:
        inst_list.append(instance.id)
    return inst_list

def lambda_handler():
    inst_id_list=get_inst_id()
    date_now=date.today()
    for inst_id in inst_id_list:
        if get_tag_val(inst_id,"stop_date") == date_now:
            print(inst_id)

lambda_handler()
