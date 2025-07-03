"""
Author: soumyaranjan.patra@xxxxxxxx.in
Use this script for getting all RDS DB details in the AWS account.
This script checks for the current roles in current users aws config and get
DB info from each AWS role
Usage:
python get_all_rds_details.py -r <aws region code>
"""
import os
import argparse
import configparser
import boto3

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

parser = argparse.ArgumentParser(description="Get RDS DB info in CSV format")
parser.add_argument("-r", "--region", type=str, help="AWS Region Code", default="ap-south-1")
args = parser.parse_args()
REGION = args.region

FILE_NAME = "/tmp/all_rds_details.csv"
with open(FILE_NAME, 'w') as csv_file:
    csv_file.write('Account_number,Account Name,rds_instance_id,rds_instance_type,DB Name,'
                   'DB Owner,Environment,RequestedBy,Service,CreatedBy,Vertical,Subvertical,'
                   'DB Engine,DB Endpoint,DB CNAME,Storage Type,Storage Size,All Tags, COPY Tags to SNAPSHOT, Backup Retention Period\n')


def get_db_info(session):
    """
    Get RDS Db Info
    :param session:
    :return:
    """
    ext_resp = []
    db_info_list = []
    rds_client = session.client("rds", region_name="ap-south-1")
    r53_client = session.client("route53", region_name="ap-south-1")
    response = rds_client.describe_db_instances()
    ext_resp.extend(response["DBInstances"])
    while "Marker" in response:
        response = rds_client.describe_db_instances(Marker=response["Marker"])
        ext_resp.extend(response["DBInstances"])
    for instance in ext_resp:
        all_tags = []
        d = {"name": "NA", "owner": "NA", "service": "NA", "requestedby": "NA", "createdby": "NA",
             "vertical": "NA", "subvertical": "NA", "env": "NA"}
        tags = instance["TagList"]
        endpoint = instance["Endpoint"]["Address"]
        copy_tags_to_snapshot = instance.get('CopyTagsToSnapshot', False)
        backup_retention_period = instance.get('BackupRetentionPeriod', 0)
        cname = get_cname_value(endpoint, r53_client)
        for tag in tags:
            tag_key = tag["Key"]
            tag_val = tag["Value"]
            all_tags.append(f"{tag_key}::{tag_val}")
            for item in d:
                if tag_key.lower() == item.lower():
                    d[item] = tag_val
        d["db_id"] = instance["DBInstanceIdentifier"]
        d["db_type"] = instance["DBInstanceClass"]
        d["engine"] = instance["Engine"]
        d["endpoint"] = endpoint
        d["cname"] = cname
        d["all_tags"] = " | ".join(all_tags)
        d["storage_type"] = instance["StorageType"]
        d["allocated_storage"] = instance["AllocatedStorage"]
        d["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        d["backup_retention_period"] = backup_retention_period

        db_info_list.append(d)
    return db_info_list


def get_cname_value(db_cname, client):
    """
    Get CNAME record from Route53
    :param db_cname:
    :param client:
    :return:
    """
    zone_list = []
    extd_response = []
    record_name = []
    zone_response = client.list_hosted_zones()
    for zone_record in zone_response["HostedZones"]:
        zone_list.append(zone_record["Id"].split("/")[2])
    for zone in zone_list:
        response = client.list_resource_record_sets(HostedZoneId=zone)
        extd_response.extend(response["ResourceRecordSets"])
        while response['IsTruncated']:
            response = (client.list_resource_record_sets
                        (HostedZoneId=zone, StartRecordName=response["NextRecordName"]))
            extd_response.extend(response["ResourceRecordSets"])
        for record in extd_response:
            if record["Type"] == "CNAME":
                for record_value in record.get("ResourceRecords", []):
                    if record_value["Value"] == db_cname:
                        record_name.append(record["Name"])
    if record_name:
        return '|'.join(record_name)
    return "NA"


for role in roles:
    print(f"Working on role {role}")
    role_session = boto3.Session(profile_name=role, region_name=REGION)
    acct_name = role.rsplit("-", 1)[0]
    account_id = role_session.client('sts').get_caller_identity().get('Account')
    dbs_info_list = get_db_info(role_session)
    with open(FILE_NAME, 'a') as csv_file:
        for db_info in dbs_info_list:
            db_instance_id = db_info["db_id"]
            db_instance_type = db_info["db_type"]
            name_tag = db_info["name"]
            owner_tag = db_info["owner"]
            db_engine = db_info["engine"]
            endpoint_dns = db_info["endpoint"]
            cname_records = db_info["cname"]
            requestedBy = db_info["requestedby"]
            createdBy = db_info["createdby"]
            service = db_info["service"]
            env = db_info["env"]
            vertical = db_info["vertical"]
            subvertical = db_info["subvertical"]
            storage_type = db_info["storage_type"]
            storage_size = db_info["allocated_storage"]
            TAGS = db_info["all_tags"]
            copy_tags_to_snapshot = db_info["copy_tags_to_snapshot"]
            backup_retention_period = db_info["backup_retention_period"]
            csv_file.write(
                f'{account_id},{acct_name},{db_instance_id},{db_instance_type},{name_tag},{owner_tag},{env},'
                f'{requestedBy},{service},{createdBy},{vertical},{subvertical},{db_engine},'
                f'{endpoint_dns},{cname_records},{storage_type},{storage_size},{TAGS},{copy_tags_to_snapshot},{backup_retention_period}\n')

print(f"File created at {FILE_NAME}")
