import configparser
import boto3

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
roles = config.sections()


def list_nat_gateways_without_name_tag(role_name):
    session = boto3.Session(profile_name=role_name, region_name="ap-south-1")
    ec2_client = session.client('ec2')

    response = ec2_client.describe_nat_gateways()

    nat_gateways_without_name = []

    for nat_gateway in response['NatGateways']:
        tags = nat_gateway.get('Tags', [])

        has_name_tag = any(tag['Key'] == 'Name' for tag in tags)

        if not has_name_tag:
            nat_gateways_without_name.append(nat_gateway)

    return nat_gateways_without_name


if __name__ == "__main__":
    for role in roles:
        nat_gateways = list_nat_gateways_without_name_tag(role)
        if nat_gateways:
            print("NAT Gateways without a 'Name' tag:")
            for nat_gateway in nat_gateways:
                print(f"NAT Gateway ID: {nat_gateway['NatGatewayId']}")
        else:
            print("All NAT Gateways have a 'Name' tag.")
