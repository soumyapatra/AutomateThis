import boto3
from datetime import datetime, timedelta
import configparser
import os

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

for role in roles:
    role_session = boto3.Session(profile_name=role)
    ce = role_session.client('ce')
    account_id = role_session.client('sts').get_caller_identity().get('Account')
    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 7, 1)

    start = start_date.strftime('%Y-%m-%d')
    end = end_date.strftime('%Y-%m-%d')
    try:
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={
                'And': [
                    {
                        'Dimensions': {
                            'Key': 'SERVICE',
                            'Values': ['AmazonCloudWatch']
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'OPERATION',
                            'Values': ['GetMetricStatistics']
                        }
                    }
                ]
            },
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'OPERATION'
                }
            ]
        )

        # Print the monthly costs
        for month in response['ResultsByTime']:
            start = month['TimePeriod']['Start']
            end = month['TimePeriod']['End']
            cost = month['Groups'][0]['Metrics']['UnblendedCost']['Amount']
            print(f"Role: {role}  Account:{account_id}  Cost: ${cost}")

    except IndexError:
        print(response)

