import boto3

ec2 = boto3.client('ec2')


def get_inst_from_tag(tag_key):
    response = ec2.describe_instances(Filters=[{'Name': 'tag-key', "Values": [tag_key]}])
    instances = response['Reservations']
    for instance in instances:
        for item in instance['Instances']:
            instance_id = item['InstanceId']
            attach_iam_prof(instance_id)
            if "IamInstanceProfile" in item:
                print("IAM_PROFILE", item['IamInstanceProfile'])


get_inst_from_tag('pt_tp')


def attach_iam_prof(inst_id):
    response = ec2.associate_iam_instance_profile(
        IamInstanceProfile={'Arn': 'arn',
                            'Name': 'Instance_describe_role'},
        InstanceId=inst_id)
    return response

