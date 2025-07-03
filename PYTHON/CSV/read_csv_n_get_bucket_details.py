import argparse
import os
import re
import pandas as pd
import boto3
import csv

parser = argparse.ArgumentParser(description="Read csv file and get bucket details")
parser.add_argument("-r", "--file-name", type=str, help="File path", required=True)
args = parser.parse_args()

home_dir = os.path.expanduser('~')
file_path = f'{args.file_name}'


def list_all_folders_with_size_and_latest_object(bucket_name, role_name, region_name):
    session = boto3.Session(profile_name=role_name, region_name=region_name)
    s3 = session.client('s3')

    # Initialize variables
    continuation_token = None
    folder_details = {}
    file_details = []

    while True:
        # List objects in the specified S3 bucket with pagination
        list_objects_params = {
            'Bucket': bucket_name,
            'Delimiter': '/'
        }
        if continuation_token:
            list_objects_params['ContinuationToken'] = continuation_token

        response = s3.list_objects_v2(**list_objects_params)

        # Check if the response contains CommonPrefixes (which are the folder names)
        if 'CommonPrefixes' in response:
            folders = [prefix['Prefix'] for prefix in response['CommonPrefixes']]

            for folder in folders:
                folder_size = 0
                latest_object = None
                latest_object_date = None
                object_count = 0
                folder_continuation_token = None

                while True:
                    list_folder_objects_params = {
                        'Bucket': bucket_name,
                        'Prefix': folder
                    }
                    if folder_continuation_token:
                        list_folder_objects_params['ContinuationToken'] = folder_continuation_token

                    folder_response = s3.list_objects_v2(**list_folder_objects_params)

                    if 'Contents' in folder_response:
                        for obj in folder_response['Contents']:
                            folder_size += obj['Size']
                            object_count += 1
                            if latest_object_date is None or obj['LastModified'] > latest_object_date:
                                latest_object_date = obj['LastModified']
                                latest_object = obj['Key']

                    if folder_response.get('IsTruncated'):
                        folder_continuation_token = folder_response.get('NextContinuationToken')
                    else:
                        break

                folder_details[folder] = {
                    'size_gb': folder_size / (1024 ** 3),  # Convert bytes to GB
                    'latest_object': latest_object,
                    'latest_object_date': latest_object_date,
                    'object_count': object_count
                }
        if 'Contents' in response and not response.get('CommonPrefixes'):
            for obj in response['Contents']:
                file_details.append({
                    'file_name': obj['Key'],
                    'size_gb': obj['Size'] / (1024 ** 3),  # Convert bytes to GB
                    'last_modified': obj['LastModified']
                })

        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

    return folder_details,file_details


def write_to_csv(folder_details, file_details, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['Folder/File', 'Size (GB)', 'Latest Object/Last Modified', 'Latest Object Date', 'Object Count'])
        for folder, details in folder_details.items():
            writer.writerow([folder, details['size_gb'], details['latest_object'], details['latest_object_date'],
                             details['object_count']])
        for file in file_details:
            writer.writerow([file['file_name'], file['size_gb'], file['last_modified'], '', ''])


df = pd.read_csv(file_path, keep_default_na=False)

for index, row in df.iterrows():
    acct_name = row["Account Name"]
    bucket_name = row["Bucket Name"]
    bucket_region = "ap-south-1"
    role_name = f"{acct_name}-role"
    output_file = f'{home_dir}/{acct_name}_bucket_details/{bucket_name}.csv'
    print(f"Working on bucket {bucket_name}")
    folder_details, file_details = list_all_folders_with_size_and_latest_object(bucket_name, role_name, bucket_region)
    if folder_details or file_details:
        write_to_csv(folder_details, file_details,output_file)
        print(f"Details have been written to {output_file}")
    else:
        print("No folders or files found in the bucket.")
