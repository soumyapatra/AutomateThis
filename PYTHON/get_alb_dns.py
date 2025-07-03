import boto3
import configparser

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
file_name = f"/tmp/all_alb_details.csv"
f = open(file_name, 'w')
f.write(f'Account_number,DNS_NAME\n')
f.close()

roles = config.sections()

for role in roles:
    print("Role Name: ", role)
    session = boto3.Session(profile_name=role)
    alb_client = session.client("elbv2", region_name="ap-south-1")
    account_id = session.client('sts').get_caller_identity().get('Account')
    albs = alb_client.describe_load_balancers()['LoadBalancers']
    alb_dns_names = [alb['DNSName'] for alb in albs if alb['Type'] == 'application']
    for dns_name in alb_dns_names:
        print(account_id,dns_name)
