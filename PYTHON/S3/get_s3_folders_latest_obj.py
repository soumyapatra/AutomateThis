import argparse
import csv
import boto3

parser = argparse.ArgumentParser(description="Provide vault details")
parser.add_argument("-r", "--role-name", type=str, help="AWS Role", required=True)
parser.add_argument("-b", "--bucket-name", type=str, help="S3 Bucket Name", required=True)
parser.add_argument("-a", "--region", type=str, help="AWS region", required=False, default="ap-south-1")
args = parser.parse_args()


def list_all_folders_with_size_and_latest_object(bucket_name, role_name, region_name):
    session = boto3.Session(profile_name=role_name, region_name=region_name)
    s3 = session.client('s3')

    # Initialize variables
    continuation_token = None
    folder_details = {}

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

        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

    return folder_details


def write_to_csv(folder_details, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Folder', 'Size (GB)', 'Latest Object', 'Latest Object Date', 'Object Count'])
        for folder, details in folder_details.items():
            writer.writerow([folder, details['size_gb'], details['latest_object'], details['latest_object_date'], details['object_count']])


bucket_name = args.bucket_name
output_file = f'{bucket_name}.csv'
folder_details = list_all_folders_with_size_and_latest_object(bucket_name, args.role_name, args.region)
if folder_details:
    write_to_csv(folder_details, output_file)
    print(f"Folder details have been written to {output_file}")
else:
    print("No folders found in the bucket.")
