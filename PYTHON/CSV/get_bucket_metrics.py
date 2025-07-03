import boto3
import csv
import datetime
import argparse

parser = argparse.ArgumentParser(description="Provide vault details")
parser.add_argument("-r", "--role-name", type=str, help="AWS Role", required=True)
parser.add_argument("-b", "--bucket-name", type=str, help="S3 Bucket Name", required=True)
parser.add_argument("-a", "--region", type=str, help="AWS region", required=False, default="ap-south-1")
args = parser.parse_args()

session = boto3.Session(profile_name=args.role_name, region_name=args.region)
cloudwatch = boto3.client('cloudwatch')

bucket_name = args.bucket_name
metric_name = 'BucketSizeBytes'
namespace = 'AWS/S3'

date = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
end_time = date
start_time = date - datetime.timedelta(days=28)
period = 86400  # 1 day in seconds


def get_bucket_size_n_obj(name, session):
    """
    Get AWS bucket size and object count using CLOUDWATCH
    :param name:
    :param session:
    :return:
    """
    cw_client = session.client('cloudwatch')
    d = {"size": "NA", "obj_count": "NA", "str_cost": "NA"}
    response_size = cw_client.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='BucketSizeBytes',
        Dimensions=[
            {'Name': 'BucketName', 'Value': name},
            {'Name': 'StorageType', 'Value': 'StandardStorage'}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=['Average']
    )
    data_points = response_size['Datapoints']
    return data_points


data_points = get_bucket_size_n_obj(bucket_name, session)

data_points.sort(key=lambda x: x['Timestamp'])

diff_list = []

csv_file = f'{bucket_name}_metrics.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'AverageBucketSizeBytes', 'DiffFromPrevious'])
    previous_val = 0
    for data_point in data_points:
        current_val = int(data_point["Average"])
        if previous_val == 0:
            diff = 0
        else:
            diff = current_val - previous_val
        writer.writerow([data_point['Timestamp'], current_val, diff])
        diff_list.append(diff)
        previous_val = current_val

avg_diff = 0
avg_diff_gb = 0
if diff_list:
    avg_diff = sum(diff_list) / len(diff_list)
    avg_diff_gb = avg_diff / (1024 ** 3)

print(f"Metrics saved to {csv_file}")

print(f"Bucket Name: {bucket_name} , Average Bytes in GB per Day: {avg_diff_gb}")