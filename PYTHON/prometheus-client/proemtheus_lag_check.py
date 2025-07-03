import boto3
import requests
from datetime import datetime
from botocore.config import Config

REGION = 'ap-south-1'
NAMESPACE = 'EC2/KAFKA_TOPICS'

URL = "http://10.14.27.32:9090/api/v1/query"

config = Config(
    retries=dict(
        max_attempts=10
    )
)


def get_data(url, query):
    PARAMS = {'query': query}
    r = requests.get(url=url, params=PARAMS)
    if r.status_code == 200:
        print("Success")
    else:
        print("Failed")
    return r.json()


query_lag = 'sum(kafka_consumergroup_lag) by (consumergroup, instance, topic)'
up_query = 'up'
query_lag_data = get_data(URL, up_query)

print(query_lag_data)
