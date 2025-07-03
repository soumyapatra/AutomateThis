import boto3


s3=boto3.client('s3')
def get_bucket_list():
    bucket_list = []
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        bucket_list.append(bucket['Name'])
    return bucket_list


def get_policy_status(bucket_name):
    response = s3.get_bucket_policy_status(Bucket=bucket_name)
    return response['PolicyStatus']

buck_list = get_bucket_list()
print(buck_list)

for bucket in buck_list:
    print(bucket,get_policy_status(bucket))
