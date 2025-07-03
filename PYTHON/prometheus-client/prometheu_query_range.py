# For getting json result of the prometheus query for last 1 week from today or setting manual date values

import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta

NO_OF_DAYS = 7
YEAR = 2020
MONTH = 1
DAY = 9

# now_date = datetime.now()
now_date = datetime(YEAR, MONTH, DAY)
previous_date = now_date - timedelta(NO_OF_DAYS)

now_date_unix = now_date.strftime("%s")
previous_date_unix = previous_date.strftime("%s")

RANGE_URL = "http://10.200.23.206/api/v1/query_range"

# Lag Query
lag_query = "2"
PARAM = {'query': lag_query, 'start': previous_date_unix, 'end': now_date_unix, 'step': '60s'}
r = requests.get(url=RANGE_URL, params=PARAM, auth=HTTPBasicAuth('devops', 'pRom@devops247'))
result = r.json()
FILENAME = f'kafka_consumer_lag_{previous_date.strftime("%Y")}_{previous_date.strftime("%m")}_{previous_date.strftime("%d")}_to_{now_date.strftime("%Y")}_{now_date.strftime("%m")}_{now_date.strftime("%d")}.json'
with open(FILENAME, 'w') as outfile:
    json.dump(result, outfile)
