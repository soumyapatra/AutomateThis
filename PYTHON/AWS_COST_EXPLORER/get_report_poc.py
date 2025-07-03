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

DAYS = 1
GRANULARITY = "DAILY"
SES_REGION = "ap-southeast-1"
EC2_REGION = "ap-south-1"


def getInstanceTag(region, tag_val):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_iterator = ec2.instances.filter(Filters=[{'Name': 'tag-key', 'Values': [tag_val]}])
    tags_list = []
    for instance in instance_iterator:
        tags = instance.tags
        for tag in tags:
            if tag['Key'] == tag_val:
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

    def addEc2Report(self, Name="Default", GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}, ],
                     Style='Total', NoCredits=True, CreditsOnly=False, RefundOnly=False, UpfrontOnly=False,
                     IncSupport=False, TagKey=""):
        type = 'chart'
        #tags = getInstanceTag(EC2_REGION, TagKey)
        tags = ['stage']
        data_row = []
        rows = []

        for tag in tags:
            print(tag)
            results = []
            Filter = {"And": [{"Tags": {"Key": "Environment", "Values": [tag]}},
                              {"Dimensions": {"Key": "REGION", "Values": ["ap-south-1"]}}]}

            response = self.client.get_cost_and_usage_with_resources(
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
                print(results)
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
        print(rows)
        df = pd.DataFrame(rows)
        df.set_index("Env", inplace=True)
        df = df.fillna(0.0)
        df = df.sort_values(by="Amazon Elastic Compute Cloud - Compute", ascending=False)
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
            s3.upload_file(filename, os.environ.get('S3_BUCKET'), filename)
        if os.environ.get('SES_SEND'):
            # Email logic
            msg = MIMEMultipart()
            msg['From'] = os.environ.get('SES_FROM')
            msg['To'] = COMMASPACE.join(os.environ.get('SES_SEND').split(","))
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "Cost Explorer Report - Environment "
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
    costexplorer = CostExplorer(CurrentMonth=False)
    print(costexplorer.addEc2Report(Name="EC2-Environment", GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
                                  Style='Total',
                                  TagKey='Environment'))


if __name__ == '__main__':
    main_handler()
