import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta

now_time = datetime(2020,3,2,7)
pre_time = now_time - timedelta(hours=4)

now_time_unix = now_time.strftime("%s")
pre_time_unix = pre_time.strftime("%s")


URL = "http://xxxxxxxxxx.com:29090/api/v1/query_range"


def get_data(url, query, pre_date, now_date):

    PARAM = {'query': query, 'start': pre_date, 'end': now_date, 'step': '60s'}
    r = requests.get(url=url, params=PARAM) 
    if r.status_code == 200:
        print("Success")
    else:
        print("Failed")
    return r.json()


count = 100

while count > 1:
    query = f'sum(avalanche_metric_mmmmm_0_{count})  by (instance,job)'
    query_data = get_data(URL, query, pre_time_unix, now_time_unix)
    if query_data['status'] == "success":
        result = query_data['data']['result']
        for item in result:
            print(item)
    count -= 1
