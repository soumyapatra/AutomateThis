#!/usr/bin/env python3

# Outputs all loggroups with > 1GB of incomingBytes in the past 7 days

import boto3
from datetime import datetime as dt
from datetime import timedelta

logs_client = boto3.client('logs')
cloudwatch_client = boto3.client('cloudwatch')

end_date = dt.today().isoformat(timespec='seconds')
start_date = (dt.today() - timedelta(days=20)).isoformat(timespec='seconds')
print("looking from %s to %s" % (start_date, end_date))

paginator = logs_client.get_paginator('describe_log_groups')
pages = paginator.paginate()
for page in pages:
    for json_data in page['logGroups']:
        log_group_name = json_data.get("logGroupName")

        cw_response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Logs',
            MetricName='IncomingBytes',
            Dimensions=[
                {
                    'Name': 'LogGroupName',
                    'Value': log_group_name
                },
            ],
            StartTime=start_date,
            EndTime=end_date,
            Period=3600 * 7,
            Statistics=[
                'Sum'
            ],
            Unit='Bytes'
        )
        if len(cw_response.get("Datapoints")):
            stats_data = cw_response.get("Datapoints")[0]
            stats_sum = stats_data.get("Sum")
            sum_GB = stats_sum / (1000 * 1000 * 1000)
            if sum_GB > 1.0:
                print("%s = %.2f GB" % (log_group_name, sum_GB))
