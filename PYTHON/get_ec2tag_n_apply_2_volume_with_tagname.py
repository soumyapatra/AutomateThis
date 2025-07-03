import configparser
import os

import boto3

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

tag_keys = ["service"]


def copy_specific_ec2_tags_to_volumes(instance_id, tag_keys):
    try:
        ec2 = session.client("ec2")
        # ec2 = boto3.client('ec2')

        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        instance_tags = instance.get('Tags', [])
        #print(f"instance tags: {instance_tags}")

        if not instance_tags:
            print(f"No tags found on instance {instance_id}")
            return

        spot_tag_key = "spotinst:accountId"

        tags_to_apply = [tag for tag in instance_tags if tag['Key'] in tag_keys]
        spot_tags = [tag for tag in instance_tags if tag['Key'] in spot_tag_key]
        #print(f"Spot Tags: {spot_tags}")
        #print(f"Tags to apply: {tags_to_apply}")

        if not tags_to_apply:
            print(f"No matching tags found on instance {instance_id} for the specified keys: {tag_keys}")
            return
        if len(spot_tags) > 0:
            print(f"Ignoring spot instance with tag {spot_tags}")
            return

        volume_ids = [device['Ebs']['VolumeId'] for device in instance['BlockDeviceMappings'] if 'Ebs' in device]
        print(f"Volume ids: {volume_ids}")

        if not volume_ids:
            print(f"No volumes attached to instance {instance_id}")
            return

        for volume_id in volume_ids:
            print(f"Volume: {volume_id}")
            # volume_tags_response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [volume_id]}])
            volume_tags_response = ec2.describe_tags(
                Filters=[
                    {'Name': 'resource-id', 'Values': [volume_id]},
                    {'Name': 'resource-type', 'Values': ['volume']}
                ]
            )
            volume_tags = volume_tags_response.get('Tags', [])
            #print(f"Volume Tags: {volume_tags}")
            volume_tag_keys = {tag['Key'] for tag in volume_tags}
            #print(f"Volume tag key: {volume_tag_keys}")

            tags_to_add = [tag for tag in tags_to_apply if tag['Key'] not in volume_tag_keys]
            #print(f"Tags to add: {tags_to_add}")

            if tags_to_add:
                # ec2.create_tags(Resources=[volume_id], Tags=tags_to_add)
                print(f"Applied tag {tags_to_add} to volume {volume_id}")
            else:
                print(f"No new tags to apply to volume {volume_id}")
    except Exception as e:
        print(f"Got error: {e}\nResponse: {response}")


if __name__ == "__main__":
    for role in roles:
        if "prod" in role:
            session = boto3.Session(profile_name=role, region_name="ap-south-1")
            ec2_client = session.client('ec2')
            ec2_instances = ec2_client.describe_instances()['Reservations']
            for reservation in ec2_instances:
                for instance in reservation['Instances']:
                    inst_id = instance['InstanceId']
                    print(f"\n-------------------------------------\nWorking on instance: {inst_id}\n"
                          f"------------------------------------")
                    copy_specific_ec2_tags_to_volumes(inst_id, tag_keys)
