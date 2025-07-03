import configparser
import os
import boto3
import csv

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

required_tags_key = ["Name", "clusters", "service", "owner", "requestedby", "env", "createdby", "component", "vertical",
                     "subvertical"]


def get_rds_tags(role_name):
    session = boto3.Session(profile_name=role_name, region_name="ap-south-1")
    rds_client = session.client("rds")
    acct_name = role_name.rsplit("-", 1)[0]
    account_id = session.client('sts').get_caller_identity().get('Account')
    rds_resources = rds_client.describe_db_instances()['DBInstances']
    all_tags = []

    for rds in rds_resources:
        resource_arn = rds['DBInstanceArn']
        rds_name = rds['DBInstanceIdentifier']
        tags = rds_client.list_tags_for_resource(ResourceName=resource_arn)['TagList']

        tag_dict = {tag['Key']: tag['Value'] for tag in tags}
        tag_dict['ResourceArn'] = resource_arn  # Add the resource ARN for reference
        tag_dict['RDSName'] = rds_name
        tag_dict['Account Name'] = acct_name
        tag_dict['Account Id'] = account_id

        all_tags.append(tag_dict)

    return all_tags


def write_tags_to_csv(all_tags, output_file):
    all_keys = set()
    for tags in all_tags:
        all_keys.update(tags.keys())

    all_keys = sorted(all_keys)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()

        for tags in all_tags:
            row = {key: tags.get(key, 'NA') for key in all_keys}
            writer.writerow(row)


if __name__ == "__main__":
    output_file = 'rds_all_tags.csv'
    final_tags = []
    for role in roles:
        print(f"Working with role: {role}")
        tags_list = get_rds_tags(role)
        final_tags.extend(tags_list)
    write_tags_to_csv(final_tags, output_file)
    print(f"Tags for all RDS resources have been written to {output_file}.")
