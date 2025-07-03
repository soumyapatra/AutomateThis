import boto3
import requests
from datetime import datetime
from botocore.config import Config

REGION = 'ap-south-1'
NAMESPACE = 'EC2/KAFKA_TOPICS'

URL = "http://10.200.23.206:9090/api/v1/query"

config = Config(
    retries=dict(
        max_attempts=10
    )
)


def update_cw_metric_by_list(metric_list, region, namespace):
    cw = boto3.client('cloudwatch', region_name=region, config=config)
    cw.put_metric_data(MetricData=metric_list, Namespace=namespace)


def get_data(url, query):
    PARAMS = {'query': query}
    r = requests.get(url=url, params=PARAMS)
    if r.status_code == 200:
        print("Success")
    else:
        print("Failed")
    return r.json()


print("================================Running code on", datetime.now(),
      "=============================================")
# Running Lag Query
query_lag = 'sum(kafka_consumergroup_lag) by (consumergroup, instance, topic)'
query_lag_data = get_data(URL, query_lag)
query_lag_count = 0
temp_list = []
print('Running LAG Check')
if query_lag_data['status'] == "success":
    result = query_lag_data['data']['result']
    for item in result:
        if len(temp_list) >= 20:
            update_cw_metric_by_list(temp_list, REGION, NAMESPACE)
            temp_list = []
        metric_name = 'kafka_consumer_lag'
        metric = item['metric']
        value = int(item['value'][1])
        timestamp = item['value'][0]
        instance = metric['instance']
        if instance == "reverie-kafka":
            continue
        context = [{'Name': 'instance', 'Value': instance},
                   {'Name': 'consumer_group', "Value": metric['consumergroup']},
                   {'Name': 'topic', "Value": metric['topic']}]
        context_list = [{'MetricName': metric_name, 'Dimensions': context, 'Unit': 'None', 'Value': value}]

        temp_list.extend(context_list)
        query_lag_count += 1
    update_cw_metric_by_list(temp_list, REGION, NAMESPACE)
    temp_list = []
else:
    print("QUERY FAILED")

if query_lag_count <= 1:
    print("No Lag Data from Prometheus")

query_in_sync = 'sum(kafka_topic_partition_in_sync_replica) by (topic,instance)'
query_in_sync_data = get_data(URL, query_in_sync)
query_in_sync_count = 0
print('Running IN-SYNC Check')

if query_in_sync_data['status'] == "success":
    result = query_in_sync_data['data']['result']
    for item in result:
        if len(temp_list) >= 20:
            update_cw_metric_by_list(temp_list, REGION, NAMESPACE)
            temp_list = []
        metric_name = 'partition_in_sync_replicas'
        metric = item['metric']
        value = int(item['value'][1])
        instance = metric['instance']
        if instance == "reverie-kafka":
            continue
        context = [{'Name': 'instance', 'Value': metric['instance']}, {'Name': 'topic', "Value": metric['topic']}]
        context_list = [{'MetricName': metric_name, 'Dimensions': context, 'Unit': 'None', 'Value': value, 'Timestamp': timestamp}]
        temp_list.extend(context_list)
        query_in_sync_count += 1
    update_cw_metric_by_list(temp_list, REGION, NAMESPACE)
    temp_list = []
else:
    print("Lag Query Failed")

if query_in_sync_count <= 1:
    print("No Lag data from prometheus")