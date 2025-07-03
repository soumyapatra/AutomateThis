import requests
import boto3
from datetime import datetime

REGION = 'ap-south-1'

# URL = "http://10.200.23.206:9090/api/v1/query"
URL = "http://10.80.120.108:9090/api/v1/query"

def update_cw_metric(metric_name, value, context, region, namespace):
    cloudwatch = boto3.client('cloudwatch', region_name=region)

    # Put custom metrics
    cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': context,
                'Unit': 'None',
                'Value': value
            }
        ],
        Namespace=namespace
    )


def update_cw_metric_by_list(metric_list, region, namespace):
    cw = boto3.client('cloudwatch', region_name=region)
    cw.put_metric_data(MetricData=[metric_list], Namespace=namespace)


def get_data(url, query):
    PARAMS = {'query': query}
    r = requests.get(url=url, params=PARAMS)
    if r.status_code == 200:
        print("Success")
    else:
        print("Failed")
    return r.json()


query_broker = 'kafka_brokers'

print("================================Running code on", datetime.now(),
      "=============================================")
# Running Lag Query
query_lag = 'sum(kafka_consumergroup_lag) by (consumergroup, instance)'
query_lag_data = get_data(URL, query_lag)
query_lag_count = 0
print('Running Insync Check')
if query_lag_data['status'] == "success":
    datas = query_lag_data['data']['result']
    for data in datas:
        metric = data['metric']
        value = int(data['value'][1])
        instance = metric['instance']
        if instance == "reverie-kafka":
            continue
        context = [{'Name': 'instance', 'Value': instance},
                   {'Name': 'consumer_group', "Value": metric['consumergroup']}]
        query_lag_count += 1
        # print("CONSUMER LAG", context, value)
        # print(update_cw_metric('kafka_consumer_lag', value, context, REGION, 'EC2/KAFKA_TOPICS'))

if query_lag_count <= 1:
    print("No Lag data from prometheus\n")

# Running In Sync Export
query_in_sync = 'sum(kafka_topic_partition_in_sync_replica) by (topic,instance)'
query_in_sync_data = get_data(URL, query_in_sync)
query_in_sync_count = 0
print('Running Lag Check')
if query_in_sync_data['status'] == "success":
    datas = query_in_sync_data['data']['result']
    for data in datas:
        metric = data['metric']
        value = int(data['value'][1])
        instance = metric['instance']
        if instance == "reverie-kafka":
            continue
        context = [{'Name': 'instance', 'Value': metric['instance']}, {'Name': 'topic', "Value": metric['topic']}]
        query_in_sync_count += 1
        # print("IN SYNC PARTITIONS", context, value)
        # print(update_cw_metric('partition_in_sync_replicas', value, context, REGION, 'EC2/KAFKA_TOPICS'))

if query_in_sync_count <= 1:
    print("No InSync Data from prometheus\n")

print("====================================DONE====================================================\n\n")
