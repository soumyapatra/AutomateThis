import boto3

role_name = "lazypay-prod-role"
session = boto3.Session(profile_name=role_name, region_name="ap-south-1")


def get_folder_size(bucket_name, folder_name):
    s3 = session.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    total_size = 0
    for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_name):
        if 'Contents' in page:
            for obj in page['Contents']:
                total_size += obj['Size']

    return total_size


def process_folders_from_file(bucket_name, file_path):
    with open(file_path, 'r') as file:
        folder_names = file.readlines()

    for folder_name in folder_names:
        folder_name = folder_name.strip()
        if folder_name:
            size_in_bytes = get_folder_size(bucket_name, folder_name)
            size_in_megabytes = size_in_bytes / (1024 * 1024)
            print(f"Total size of the folder '{folder_name}' in bucket '{bucket_name}' is {size_in_megabytes:.2f} MB")


bucket_name = 's3-access-logs-lp-prod'
file_path = 'logging-prefix.txt'

process_folders_from_file(bucket_name, file_path)
