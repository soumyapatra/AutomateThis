from __future__ import print_function

__author__ = "David Faulkner"
__version__ = "0.1.3"
__license__ = "MIT No Attribution"

import os
import boto3
from datetime import date
from datetime import timedelta
import pandas as pd
from collections import defaultdict
# For date
from dateutil.relativedelta import relativedelta
# For email
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

DAYS = os.environ['DAYS']
TAG_KEYS = []
GRANULARITY = "DAILY"
SES_REGION = os.environ['SES_REGION']
EC2_REGION = os.environ['EC2_REGION']


def getInstanceTag(region, tag_key):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_iterator = ec2.instances.filter(Filters=[{'Name': 'tag-key', 'Values': [tag_key]}])
    tags_list = []
    for instance in instance_iterator:
        tags = instance.tags
        for tag in tags:
            if tag['Value'] not in tags_list:
                tags_list.append(tag['Value'])
    return tags_list


class CostExplorer:
    def __init__(self, CurrentMonth=False):
        # Array of reports ready to be output to Excel.
        self.reports = []
        self.client = boto3.client('ce', region_name='us-east-1')
        self.start = date.today() - timedelta(days=int(DAYS))
        self.end = date.today()

    def addEc2Report(self, Name="Default", GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
                     Style='Total', NoCredits=True, CreditsOnly=False, RefundOnly=False, UpfrontOnly=False,
                     IncSupport=False, TagKey="", TagVal=""):
        type = 'chart'
        tags = getInstanceTag(EC2_REGION, TagKey)
        # tags = ['docker-9tzkzu', 'abc123', 'ab9555']
        group_key = GroupBy[0]["Key"]
        row = {group_key: [], 'Cost': []}
        results = []
        Filter = {"And": [{"Tags": {"Key": TagKey, "Values": TagVal}},
                          {"Dimensions": {"Key": "REGION", "Values": ["ap-south-1"]}}]}
        response = self.client.get_cost_and_usage(
            TimePeriod={
                'Start': self.start.isoformat(),
                'End': self.end.isoformat()
            },
            Granularity=GRANULARITY,
            Metrics=[
                'UnblendedCost',
            ],
            GroupBy=GroupBy,
            Filter=Filter
        )
        print(response)
        if response:
            results.extend(response['ResultsByTime'])
            while 'nextToken' in response:
                nextToken = response['nextToken']
                response = self.client.get_cost_and_usage(
                    TimePeriod={
                        'Start': self.start.isoformat(),
                        'End': self.end.isoformat()
                    },
                    Granularity=GRANULARITY,
                    Metrics=[
                        'UnblendedCost',
                    ],
                    GroupBy=GroupBy,
                    NextPageToken=nextToken
                )
                results.extend(response['ResultsByTime'])
            if 'nextToken' in response:
                nextToken = response['nextToken']
            else:
                nextToken = False
            print(results)
            for v in results:
                # print(v)
                if not v['Groups']:
                    continue
                sort = v['TimePeriod']['Start']
                for i in v['Groups']:
                    key = i['Keys'][0].split("$")[-1]
                    cost = float(i['Metrics']['UnblendedCost']['Amount'])
                    row[group_key].append(key)
                    row["Cost"].append(cost)
                if not v['Groups']:
                    key = 'Total'
                    cost = float(v['Total']['UnblendedCost']['Amount'])
                    row["Application"].append(key)
                    row["Cost"].append(cost)
        sort = ''
        df = pd.DataFrame(row)
        df.set_index(group_key, inplace=True)
        df = df.fillna(0.0)
        # df = df.sort_values(by="Amazon Elastic Compute Cloud - Compute", ascending=False)
        self.reports.append({'Name': Name, 'Data': df, 'Type': type})
        return df

    def generateExcel(self):
        # Create a Pandas Excel writer using XlsxWriter as the engine.\
        os.chdir('/tmp')
        start_date = self.start
        filename = f'cost_explorer_report-{start_date}.xlsx'
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        workbook = writer.book
        for report in self.reports:
            print(report['Name'], report['Type'])
            report['Data'].to_excel(writer, sheet_name=report['Name'])
            worksheet = writer.sheets[report['Name']]
            if report['Type'] == 'chart':

                # Create a chart object.
                chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})

                chartend = 12
                for row_num in range(1, len(report['Data']) + 1):
                    chart.add_series({
                        'name': [report['Name'], row_num, 0],
                        'categories': [report['Name'], 0, 1, 0, chartend],
                        'values': [report['Name'], row_num, 1, row_num, chartend],
                    })
                chart.set_y_axis({'label_position': 'low'})
                chart.set_x_axis({'label_position': 'low'})
                worksheet.insert_chart('O2', chart, {'x_scale': 2.0, 'y_scale': 2.0})
        writer.save()
        if os.environ.get('S3_BUCKET'):
            s3 = boto3.client('s3')
            key = f"cost-report/{filename}"
            s3.upload_file(filename, os.environ.get('S3_BUCKET'), key)

    def generateCsv(self):
        os.chdir('/tmp')
        start_date = self.start
        for report in self.reports:
            name = report["Name"]
            data = report["Data"]
            filename = f'{name}-{start_date}.csv'
            print(f'Saving report: {name}')
            data.to_csv(filename, index=False)
            if os.environ.get('S3_BUCKET'):
                s3 = boto3.client('s3')
                key = f"cost-report/{filename}"
                s3.upload_file(filename, os.environ.get('S3_BUCKET'), key)


def main_handler(event=None, context=None):
    tag_key = "billing_unit"
    tag_val = ["gr_production", "gr_reverie_production"]
    costexplorer = CostExplorer(CurrentMonth=False)
    costexplorer.addEc2Report(Name="EC2: Application Tag", GroupBy=[{"Type": "TAG", "Key": "Application"}],
                              Style='Total',
                              TagKey=tag_key, TagVal=tag_val)
    costexplorer.generateCsv()
    costexplorer.generateExcel()


if __name__ == '__main__':
    main_handler()
