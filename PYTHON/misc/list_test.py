import boto3

REGION = 'ap-southeast-1'
NAMESPACE = 'ec2/KAFKA_TOPICS'


def update_cw_metric_by_list(metric_list, region, namespace):
    cw = boto3.client('cloudwatch', region_name=region)
    cw.put_metric_data(MetricData=[metric_list], Namespace=namespace)


list1 = [1, 2, 3, 4, 5, 6, 7, 5, 3, 2, 4, 5, 6, 7, 8, 3, 56, 7657, 234, 42654645, 132, 345345, 213, 45, 56, 67675]
temp_list = []

for item in list1:
    if len(temp_list) >= 5:
        print(temp_list, '\n')
        temp_list = []
    context = [{'item': item}]
    temp_list.extend(context)
