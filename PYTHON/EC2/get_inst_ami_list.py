import boto3


def get_inst_ami_list(region):
    ami_list = []
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances()

    for instance in response['Reservations']:
        ami_id = instance['Instances'][0]['ImageId']
        print('AMI_ID:',ami_id)
        ami_name = get_ami_name(ami_id)
        print('AMI_NAME:',ami_name)
        if ami_name not in ami_list:
            ami_list.append(ami_name)
    return ami_list


def get_ami_name(ami_id):
    ec2 = boto3.client('ec2',region_name='ap-south-1')
    response = ec2.describe_images(ImageIds=[ami_id])
    for element in response['Images']:
        return element['Name']


print(get_inst_ami_list('ap-south-1'))
