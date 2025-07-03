import boto3


def copy_instance_tags_to_volumes(role_name):
    session = boto3.Session(profile_name=role_name,region_name="ap-south-1")
    ec2 = session.resource('ec2')

    instances = ec2.instances.all()

    for instance in instances:
        instance_id = instance.id
        instance_tags = instance.tags

        if not instance_tags:
            print(f"No tags found for instance {instance_id}")
            continue
        if any(tag['Key'] == 'spotinst:accountId' for tag in instance_tags):
            print(f"Skipping instance {instance_id} with tag key 'spotinst:accountId'")
            continue
        instance_tags = [tag for tag in instance_tags if not tag['Key'].startswith('aws')]

        volumes = instance.volumes.all()

        for volume in volumes:
            volume_tags = volume.tags if volume.tags else []
            volume_tag_keys = {tag['Key'] for tag in volume_tags}

            tags_to_add = [tag for tag in instance_tags if tag['Key'] not in volume_tag_keys]

            if tags_to_add:
                #volume.create_tags(Tags=tags_to_add)
                print(f"Copied tags {tags_to_add} to volume {volume.id} from instance {instance_id}")
            else:
                print(f"All instance tags already present on volume {volume.id} for instance {instance_id}")


if __name__ == "__main__":
    copy_instance_tags_to_volumes("xxxxxxxxfin-sbox-role")