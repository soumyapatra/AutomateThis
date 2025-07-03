import boto3

ad=boto3.client('ec2')

response=ad.describe_addresses()

for address in response['Addresses']:
    if 'AssociationId' not in address:
        print(address)
