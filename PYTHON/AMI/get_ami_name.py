
import boto3

def get_ami_name(ami_id):
    ec2 = boto3.client('ec2')
    response = ec2.describe_images(ImageIds=[ami_id])
    return response['Images'][0]['Name']


print(get_ami_name('ami-082aee40b2844e35b'))
