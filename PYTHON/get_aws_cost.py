import boto3
import pandas as pd
from datetime import datetime, timedelta
import configparser
import os

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

end_date = datetime.today().replace(day=1)
start_date = (end_date - timedelta(days=1)).replace(day=1)

time_period = {
    'Start': start_date.strftime('%Y-%m-%d'),
    'End': end_date.strftime('%Y-%m-%d')
}
costs_list = []

for role in roles:
    print(f"Working on profile: {role}")
    session = boto3.Session(profile_name=role)
    ce = session.client("ce")
    acct_name = role.rsplit("-", 1)[0]
    account_id = session.client('sts').get_caller_identity().get('Account')
    response = ce.get_cost_and_usage(
        TimePeriod=time_period,
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    #service_costs = {"Account Name" : acct_name, "Account Id": account_id}
    service_costs = {"Account Name": acct_name}
    costs = response['ResultsByTime'][0]['Groups']
    for item in costs:
        service_name = item['Keys'][0]
        cost_amount = float(item['Metrics']['UnblendedCost']['Amount'])
        formatted_cost = round(cost_amount, 4) if cost_amount >= 0.0001 else 0
        service_costs[service_name] = formatted_cost
    costs_list.append(service_costs)

df = pd.DataFrame(costs_list)
df['MaxCostService'] = df.drop(columns=['Account Name']).idxmax(axis=1)
df = df.set_index('Account Name')
df = df.reindex(
    columns=['MaxCostService'] + df.drop(columns=['MaxCostService']).max().sort_values(ascending=False).index.tolist())
df = df.reset_index()
csv_file = 'aws_costs_previous_month.csv'
df.to_csv(csv_file, index=False)

print(f'CSV file {csv_file} has been created.')
