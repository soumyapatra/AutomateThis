import configparser
import os

import boto3
import argparse

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()
role_names = [a.replace("-role", "") for a in roles]

role_name_string = ",".join(role_names)


def tag_instance(instance_id, tag_key, tag_value, role_name, region):
    session = boto3.Session(profile_name=role_name, region_name=region)
    ec2 = session.client('ec2', region_name=region)

    response = ec2.describe_instances(InstanceIds=[instance_id])

    instances = response['Reservations'][0]['Instances']
    if not instances:
        print(f"No instance found with ID: {instance_id}")
        return

    instance = instances[0]
    current_tags = instance.get('Tags', [])

    for tag in current_tags:
        if tag['Key'] == tag_key:
            print(f"Tag '{tag_key}' already present with value '{tag['Value']}'.")
            return

    #    ec2.create_tags(
    #        Resources=[instance_id],
    #        Tags=[{'Key': tag_key, 'Value': tag_value}]
    #    )
    print(f"Tag '{tag_key}' with value '{tag_value}' added to instance '{instance_id}'.")


def parseargs(role_names):
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                        description="Tag an EC2 instance if the tag is not present.")
    argparser.add_argument("--acct", help=f"The AWS account from {role_names}")
    argparser.add_argument("--instance_id", help="The ID of the EC2 instance to tag.")
    argparser.add_argument("--key", help="The key of the tag to check/add.")
    argparser.add_argument("--value", help="The value of the tag to add if not present.")
    argparser.add_argument("--region", help="The AWS region of the instance. Default is 'ap-south-1'", required=False, default="ap-south-1")
    return argparser.parse_args()


if __name__ == "__main__":
    args = parseargs(role_name_string)
    inst_id = args.instance_id
    role_name = args.acct
    key = args.key
    value = args.value
    region = args.region


    tag_instance(inst_id, key, value, role_name, region)
