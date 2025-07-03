import boto3
session = boto3.Session(profile_name="lazypay-prod-role")
s3 = boto3.client('s3')

bucket_name = 's3-access-logs-lp-prod'

total_size = 0
earliest_date = None
latest_date = None

continuation_token = None

while True:
    if continuation_token:
        response = s3.list_objects_v2(Bucket=bucket_name, ContinuationToken=continuation_token)
    else:
        response = s3.list_objects_v2(Bucket=bucket_name)

    for obj in response.get('Contents', []):
        total_size += obj['Size']
        obj_date = obj['LastModified']

        if earliest_date is None or obj_date < earliest_date:
            earliest_date = obj_date
        if latest_date is None or obj_date > latest_date:
            latest_date = obj_date

    if response.get('IsTruncated'):
        continuation_token = response.get('NextContinuationToken')
    else:
        break

if earliest_date and latest_date:
    date_range = (latest_date - earliest_date).days + 1  # +1 to include both start and end dates
else:
    date_range = 1  # Default to 1 to avoid division by zero

average_data_per_day = total_size / date_range

average_data_per_day_mb = average_data_per_day / (1024 * 1024)

print(f"Total size of data uploaded: {total_size} bytes")
print(f"Date range: {date_range} days")
print(f"Average data uploaded per day: {average_data_per_day_mb:.2f} MB")
