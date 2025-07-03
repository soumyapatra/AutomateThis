import boto3
import requests
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


def run_lag_check(query, url):
    response = get_data(url, query)
    count = 0
    temp_list = []
    print('Running LAG Check')
    if response['status'] == "success":
        result = response['data']['result']
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
            context_list = [{'MetricName': metric_name, 'Dimensions': context, 'Unit': 'None', 'Value': value,
                             'Timestamp': timestamp}]
            temp_list.extend(context_list)
            count += 1
        update_cw_metric_by_list(temp_list, REGION, NAMESPACE)
        temp_list = []
    else:
        print("QUERY FAILED")
    if count <= 1:
        print("No Data from Prometheus")


def run_insync_check(query, url):
    response = get_data(url, query)
    count = 0
    temp_list = []
    print('Running IN-SYNC Check')
    if response['status'] == "success":
        result = response['data']['result']
        for item in result:
            if len(temp_list) >= 20:
                update_cw_metric_by_list(temp_list, REGION, NAMESPACE)
                temp_list = []
            metric_name = 'partition_in_sync_replicas'
            metric = item['metric']
            value = int(item['value'][1])
            timestamp = item['value'][0]
            instance = metric['instance']
            if instance == "reverie-kafka":
                continue
            context = [{'Name': 'instance', 'Value': metric['instance']}, {'Name': 'topic', "Value": metric['topic']}]
            context_list = [
                {'MetricName': metric_name, 'Dimensions': context, 'Unit': 'None', 'Value': value,
                 'Timestamp': timestamp}]
            temp_list.extend(context_list)
            count += 1
        update_cw_metric_by_list(temp_list, REGION, NAMESPACE)
        temp_list = []
    else:
        print("Lag Query Failed")

    if count <= 1:
        print("No data from prometheus")


def lambda_handler(event, context):
    query_lag = 'sum(kafka_consumergroup_lag) by (consumergroup, instance, topic)'
    query_sync_check = 'sum(kafka_topic_partition_in_sync_replica) by (topic,instance)'
    run_lag_check(query_lag, URL)
    run_insync_check(query_sync_check, URL)
