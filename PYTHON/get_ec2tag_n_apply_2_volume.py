import boto3

role_name = "xxxxxxxxfin-sbox-role"

session = boto3.Session(profile_name=role_name,region_name="ap-south-1")


def copy_ec2_tags_to_volumes(instance_id):
    ec2 = session.client("ec2")

    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]

    instance_tags = instance.get('Tags', [])

    if not instance_tags:
        print(f"No tags found on instance {instance_id}")
        return

    volume_ids = [device['Ebs']['VolumeId'] for device in instance['BlockDeviceMappings'] if 'Ebs' in device]

    if not volume_ids:
        print(f"No volumes attached to instance {instance_id}")
        return

    for volume_id in volume_ids:
        print(f"Got vol id: {volume_id}")
        volume_tags_response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [volume_id]}])
        volume_tags = volume_tags_response.get('Tags', [])
        volume_tag_keys = {tag['Key'] for tag in volume_tags}

        tags_to_add = [tag for tag in instance_tags if tag['Key'] not in volume_tag_keys]
        

        if tags_to_add:
        #    ec2.create_tags(Resources=[volume_id], Tags=tags_to_add)
            print(f"Applied new tags to volume {volume_id}")
        else:
            print(f"No new tags to apply to volume {volume_id}")


if __name__ == "__main__":
    instance_id = "i-xxxxxxxxxxxxxxxxx"  # Replace with your EC2 instance ID
    copy_ec2_tags_to_volumes(instance_id)
