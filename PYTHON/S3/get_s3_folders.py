import argparse

import boto3
import csv

parser = argparse.ArgumentParser(description="Provide vault details")
parser.add_argument("-r", "--role-name", type=str, help="AWS Role", required=True)
parser.add_argument("-b", "--bucket-name", type=str, help="S3 Bucket Name", required=True)
parser.add_argument("-a", "--region", type=str, help="AWS region", required=False, default="ap-south-1")
args = parser.parse_args()


def list_all_folders_with_size(bucket_name, role_name, region):
    session = boto3.Session(profile_name=role_name, region_name=region)
    s3 = session.client('s3')

    continuation_token = None
    folder_sizes = {}

    while True:
        list_objects_params = {
            'Bucket': bucket_name,
            'Delimiter': '/'
        }
        if continuation_token:
            list_objects_params['ContinuationToken'] = continuation_token

        response = s3.list_objects_v2(**list_objects_params)

        if 'CommonPrefixes' in response:
            folders = [prefix['Prefix'] for prefix in response['CommonPrefixes']]

            for folder in folders:
                folder_size = 0
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

                    if folder_response.get('IsTruncated'):
                        folder_continuation_token = folder_response.get('NextContinuationToken')
                    else:
                        break

                folder_sizes[folder] = folder_size / (1024 ** 3)  # Convert bytes to GB

        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

    return folder_sizes


def write_to_csv(folder_sizes, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Folder', 'Size (GB)'])
        for folder, size in folder_sizes.items():
            writer.writerow([folder, size])


bucket_name = args.bucket_name
output_file = f'{bucket_name}.csv'
region_name = args.region
folder_sizes = list_all_folders_with_size(bucket_name, args.role_name, region_name)
if folder_sizes:
    write_to_csv(folder_sizes, output_file)
    print(f"Folder sizes have been written to {output_file}")
else:
    print("No folders found in the bucket.")
