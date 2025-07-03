"""
Get ALL EC2 details with recommendation
Please note this needs the account to be activated with AWS Compute Optimizer and
will give result post 12 hours of the above activated service
"""

import boto3
import csv
import argparse
import configparser
import os

parser = argparse.ArgumentParser(description="Get Ec2 recommendation for the role")
parser.add_argument("-p", "--role-name", type=str, help="AWS Role Name", required=True)
args = parser.parse_args()
role_name = args.role_name
region = "ap-south-1"
acct_name = role_name.rsplit("-", 1)[0]
file_name = f"/tmp/{acct_name}_ec2_instance_details.csv"
if os.path.exists(file_name):
    os.remove(file_name)

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()


def get_instance_recommendation(arn, session, region_name):
    """
    Get instance recommendations
    :param arn:
    :param session:
    :param region_name:
    :return:
    """
    client = session.client('compute-optimizer', region_name=region_name)
    recommendation_preferences = {
        'cpuVendorArchitectures': ['CURRENT']
    }
    response = client.get_ec2_instance_recommendations(instanceArns=[arn],
                                                       recommendationPreferences=recommendation_preferences)
    if response['instanceRecommendations']:
        recommendation = response["instanceRecommendations"][0]
        if recommendation["finding"] == "OVER_PROVISIONED" and len(recommendation["recommendationOptions"]) > 0:
            d = dict()
            current_instance_type = recommendation["currentInstanceType"]
            recommendation_details_list = []
            reasoncodes = []
            # print(instance_name, current_instance_type)
            # json_dump = json.dumps(recommendation, indent=4, default=datetime_converter)
            for instance_recommendation in recommendation["recommendationOptions"]:
                inst_type = instance_recommendation["instanceType"]
                inst_rank = instance_recommendation["rank"]
                inst_migration_effort = instance_recommendation["migrationEffort"]
                if inst_type != current_instance_type:
                    recommendation_details_list.append(f"{inst_type}({inst_rank})({inst_migration_effort})")

            # print(current_instance_type,recommend_instance_types)
            for reasoncode in recommendation["findingReasonCodes"]:
                reasoncodes.append(reasoncode)

            s = " | "
            recommendation_details_list_string = s.join(recommendation_details_list)
            reasoncode_string = s.join(reasoncodes)
            d["finding"] = recommendation["finding"]
            d["reasoncodes"] = reasoncode_string
            d["recommendation_details"] = recommendation_details_list_string
            return d
    return "NA"


for role in roles:
    if role == role_name:
        ec2_session = boto3.Session(profile_name=role_name)
        ec2 = ec2_session.resource('ec2', region_name=region)
        instance = ec2.instances.all()
        with open(file_name, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'InstanceId', 'State', 'PrivateIpAddress', 'PublicIpAddress',
                          'LaunchTime', 'Owner', 'Service', 'RecommendationFinding', 'RecommendationFindingReasonCode',
                          'CurrentInstanceType', 'RecommendedInstanceType(rank)(migration_effort)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            instances = ec2.instances.all()
            for instance in instances:
                recommend_instance_finding = "NA"
                recommended_inst_details = "NA"
                recommend_instance_finding_reasoncode = "NA"
                name_tag = next((tag['Value'] for tag in instance.tags if tag['Key'] == 'Name'), "NA")
                owner_tag = next((tag['Value'] for tag in instance.tags if tag['Key'] == 'owner'), "NA")
                service_tag = next((tag['Value'] for tag in instance.tags if tag['Key'] == 'service'), "NA")
                instance_arn = (f'arn:aws:REDACTED"AvailabilityZone"][:-1]}:'
                                f'{ec2_session.client("sts").get_caller_identity()["Account"]}:instance/{instance.id}')
                recommendation_data = get_instance_recommendation(instance_arn, ec2_session, region)
                if recommendation_data != "NA":
                    recommended_inst_details = recommendation_data["recommendation_details"]
                    recommend_instance_finding = recommendation_data["finding"]
                    recommend_instance_finding_reasoncode = recommendation_data["reasoncodes"]
                writer.writerow({
                    'Name': name_tag,
                    'InstanceId': instance.id,
                    'State': instance.state['Name'],
                    'PrivateIpAddress': instance.private_ip_address,
                    'PublicIpAddress': instance.public_ip_address,
                    'LaunchTime': instance.launch_time,
                    'Owner': owner_tag,
                    'Service': service_tag,
                    'RecommendationFinding': recommend_instance_finding,
                    'RecommendationFindingReasonCode': recommend_instance_finding_reasoncode,
                    'CurrentInstanceType': instance.instance_type,
                    'RecommendedInstanceType(rank)(migration_effort)': recommended_inst_details,
                })
            print(f"Instance details have been written to {file_name}")
