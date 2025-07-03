from __future__ import print_function

__author__ = "David Faulkner"
__version__ = "0.1.3"
__license__ = "MIT No Attribution"

import os
import boto3
from datetime import date
from datetime import timedelta
import pandas as pd
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
ce = boto3.client('ce', region_name='us-east-1')


def getInstanceTag(region, filter_tag, filter_tag_val, group_by_tag):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_iterator = ec2.instances.filter(Filters=[{'Name': 'tag-key', 'Values': [filter_tag, group_by_tag]}])
    tags_list = []
    for instance in instance_iterator:
        tags = instance.tags
        for tag in tags:
            if tag['Key'] == filter_tag and tag['Value'] in filter_tag_val:
                for i in tags:
                    if i["Key"] == group_by_tag:
                        if i["Value"] not in tags_list:
                            tags_list.append(i["Value"])
    return tags_list


def getCostNUsage(start_date, end_date, filters, groupby=None):
    results = []
    response = ce.client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.isoformat(),
            'End': end_date.isoformat()
        },
        Granularity=GRANULARITY,
        Metrics=[
            'UnblendedCost',
        ],
        GroupBy=groupby,
        Filter=filters
    )
    # print(response)
    if response:
        results.extend(response['ResultsByTime'])
        while 'nextToken' in response:
            nextToken = response['nextToken']
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.isoformat(),
                    'End': end_date.isoformat()
                },
                Granularity=GRANULARITY,
                Metrics=[
                    'UnblendedCost',
                ],
                GroupBy=groupby,
                NextPageToken=nextToken
            )
            results.extend(response['ResultsByTime'])
        if 'nextToken' in response:
            nextToken = response['nextToken']
        else:
            nextToken = False
        return results


class CostExplorer:
    def __init__(self, CurrentMonth=False):
        # Array of reports ready to be output to Excel.
        self.reports = []
        self.total_df = []
        self.client = boto3.client('ce', region_name='us-east-1')
        self.start = date.today() - timedelta(days=int(DAYS))
        self.end = date.today()

    def addEc2Report(self, Name="Default", GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}, ],
                     Style='Total', NoCredits=True, CreditsOnly=False, RefundOnly=False, UpfrontOnly=False,
                     IncSupport=False, TagKey="", TagVal=""):
        type = 'chart'
        tags = getInstanceTag(EC2_REGION, "billing_unit", TagVal, "Application")
        rows = []
        for tag in tags:
            results = []
            Filter = {"And": [{"Tags": {"Key": TagKey, "Values": [tag]}},
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
            # print(response)
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
                for v in results:
                    # print(v)
                    if not v['Groups']:
                        continue
                    row = {'Env': tag}
                    sort = v['TimePeriod']['Start']
                    for i in v['Groups']:
                        key = i['Keys'][0]
                        row.update({key: float(i['Metrics']['UnblendedCost']['Amount'])})
                    if not v['Groups']:
                        row.update({'Total': float(v['Total']['UnblendedCost']['Amount'])})
                    rows.append(row)
        sort = ''
        df = pd.DataFrame(rows)
        df.set_index("Env", inplace=True)
        df = df.fillna(0.0)
        df = df.sort_values(by="Amazon Elastic Compute Cloud - Compute", ascending=False)
        self.reports.append({'Name': Name, 'Data': df, 'Type': type})
        return df

    def getTotalReport(self, tagKey="", tagVal=""):
        results = []
        Filter = {"And": [{"Tags": {"Key": tagKey, "Values": tagVal}},
                          {"Dimensions": {"Key": "REGION", "Values": [EC2_REGION]}}]}
        results.extend(getCostNUsage(self.start, self.end, Filter))
        old_start = self.start - timedelta(days=1)
        old_end = self.end - timedelta(days=1)
        results.extend(getCostNUsage(old_start, old_end, Filter))
        rows = {"date": [], "cost": []}
        for v in results:
            dat = v["TimePeriod"]["Start"]
            cost = v["Total"]["UnblendedCost"]["Amount"]
            rows["date"].append(dat)
            rows["cost"].append(cost)
        df = pd.DataFrame(rows)
        df.set_index("date", inplace=True)
        df = df.fillna(0.0)
        data = {"df": df}
        self.total_df.append(data)
        return df

    def generateExcel(self, reportName=""):
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
                if self.total_df:
                    for i in self.total_df:
                        i["df"].to_excel(writer, sheet_name=report['Name'], startrow=50, startcol=0)
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
            key = f"cost_report/{filename}"
            s3 = boto3.client('s3')
            s3.upload_file(filename, os.environ.get('S3_BUCKET'), key)
        if os.environ.get('SES_SEND'):
            # Email logic
            msg = MIMEMultipart()
            msg['From'] = os.environ.get('SES_FROM')
            msg['To'] = COMMASPACE.join(os.environ.get('SES_SEND').split(","))
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = f"Cost Explorer Report - {reportName}"
            text = "Find your Cost Explorer report attached\n\n"
            msg.attach(MIMEText(text))
            with open(filename, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=filename
                )
            part['Content-Disposition'] = 'attachment; filename="%s"' % filename
            msg.attach(part)
            # SES Sending
            ses = boto3.client('ses', region_name=SES_REGION)
            result = ses.send_raw_email(
                Source=msg['From'],
                Destinations=os.environ.get('SES_SEND').split(","),
                RawMessage={'Data': msg.as_string()}
            )
            print("SES RESULTS: ", result)

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
                s3.upload_file(filename, os.environ.get('S3_BUCKET'), filename)


def main_handler(event=None, context=None):
    tag_val = ["gr_production", "gr_production"]
    costexplorer = CostExplorer(CurrentMonth=False)
    costexplorer.addEc2Report(Name="EC2 Application - GR", GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
                              Style='Total',
                              TagKey='Application', TagVal=tag_val)
    costexplorer.getTotalReport(tagKey="billing_unit", tagVal=tag_val)
    costexplorer.generateExcel(reportName="Application (DR)")


if __name__ == '__main__':
    main_handler()
