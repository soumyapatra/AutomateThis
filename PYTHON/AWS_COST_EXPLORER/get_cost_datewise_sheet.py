from __future__ import print_function

__author__ = "David Faulkner"
__version__ = "0.1.3"
__license__ = "MIT No Attribution"

import os
import json
import requests
import boto3
from datetime import date
from datetime import timedelta
import pandas as pd
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
HOOK_URL = os.environ["HOOK_URL"]
SNS_ARN = os.environ["SNS_ARN"]

def slack_send(slack_channel, message, sub, title):
    channels = []
    if slack_channel != "":
        channels.append(slack_channel)
    for channel in channels:
        slack_msg = {
            "username": "ALARM",
            "mrkdwn": 'true',
            'icon_emoji': ':robot_face:',
            "channel": channel,
            "attachments": [
                {
                    "fallback": sub,
                    "author_name": "AWS",
                    "color": "#7B68EE",
                    "title": title,
                    "text": message,
                }
            ]
        }
        try:
            requests.post(HOOK_URL, data=json.dumps(slack_msg))
        except Exception as e:
            print("Failed:", e)
            
def pub_sns(arn, msg, sub):
    sns = boto3.client('sns', region_name=EC2_REGION)
    response = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return response


def get_instance_tag(region, search_tag,  search_tag_val_list,  target_tag):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_iterator = ec2.instances.filter(Filters=[{'Name': 'tag-key', 'Values': [search_tag, target_tag]}])
    tags_list = []
    for instance in instance_iterator:
        tags = instance.tags
        for tag in tags:
            if tag["Key"] == search_tag and tag["Value"] in search_tag_val_list:
                for tag in tags:
                    if tag["Key"] == target_tag and tag["Value"] not in tags_list:
                        tags_list.append(tag["Value"] )
    return tags_list


def getCostNUsage(start_date, end_date, filters, groupby=[]):
    if groupby is None:
        groupby = []
    results = []
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
                     IncSupport=False, TagKey="", TagVal="", days_old=0):
        startdate = self.start - timedelta(days=days_old)
        enddate = self.end - timedelta(days=days_old)
        type = 'chart'
        tags = get_instance_tag(EC2_REGION, "billing_unit", TagVal, "Application")
        print(tags)
        rows = []
        for tag in tags:
            results = []
            Filter = {"And": [{"Tags": {"Key": TagKey, "Values": [tag]}},
                              {"Dimensions": {"Key": "REGION", "Values": ["ap-south-1"]}}]}

            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': startdate.isoformat(),
                    'End': enddate.isoformat()
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
                    row = {'Application': tag}
                    for i in v['Groups']:
                        key = i['Keys'][0]
                        row.update({key: float(i['Metrics']['UnblendedCost']['Amount'])})
                    if not v['Groups']:
                        row.update({'Total': float(v['Total']['UnblendedCost']['Amount'])})
                    rows.append(row)
        rows_length = len(rows)
        print(rows)
        df = pd.DataFrame(rows)
        df.set_index("Application", inplace=True)
        df = df.fillna(0.0)
        df = df.sort_values(by="Amazon Elastic Compute Cloud - Compute", ascending=False)
        self.reports.append({'Name': Name, 'Data': df, 'Type': type, 'length': rows_length})
        return df

    def getTotalReport(self, tagKey="", tagVal=""):
        results = []
        days = 3
        count = 0
        rows = {"day": [], "Total cost": []}
        Filter = {"And": [{"Tags": {"Key": tagKey, "Values": tagVal}},
                          {"Dimensions": {"Key": "REGION", "Values": [EC2_REGION]}}]}
        while count < days:
            results.extend(getCostNUsage(self.start - timedelta(days=count), self.end - timedelta(days=count), Filter))
            count += 1
        for v in results:
            dat = v["TimePeriod"]["Start"]
            cost = v["Total"]["UnblendedCost"]["Amount"]
            rows["day"].append(dat)
            rows["Total cost"].append(cost)
        df = pd.DataFrame(rows)
        df.set_index("day", inplace=True)
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
                    worksheet.write(report["length"] + 4, 0, "Previous Date Cost")
                    for i in self.total_df:
                        i["df"].to_excel(writer, sheet_name=report['Name'], startrow=report["length"] + 5, startcol=0)
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
            text = f"Find your Cost Explorer report attached for date {start_date}\nNOTE: It takes around 24 hours for billing cost to generate. Therefore Kindly refer to reports older than 24 hours for complete results.\nThese reports have been added as a sheet and named based on the date"
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
    try:
        
        tag_val = ["gr_rc_production", "gr_reverie_production"]
        costexplorer = CostExplorer(CurrentMonth=False)
        days = 3
        count = 0
        while count < days:
            report_date = date.today() - timedelta(days=count+1)
            costexplorer.addEc2Report(Name=f"Production GR - {report_date}", GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
                                      Style='Total',
                                      TagKey='Application', TagVal=tag_val, days_old=count)
            count += 1
        costexplorer.getTotalReport(tagKey="billing_unit", tagVal=tag_val)
        costexplorer.getTotalReport(tagKey="billing_unit", tagVal=tag_val)
        costexplorer.generateExcel(reportName="GR Applications (DR Account)")
    except Exception as e:
        function_name = context.function_name
        print("Got Exception: ", e)
        slack_send("lambda_alerts", f"Issue in Lambda function {function_name}\nIssue: {e}",
                   f"Issue in Lambda: {function_name}", "Lambda Issue")
        msg = f'Issue while creating cost report\nIssue in Lambda function: {function_name}\nIssue: {e}'
        sub = f'Lambda Execution Failed; {function_name}'
        print(pub_sns(SNS_ARN, msg, sub))

if __name__ == '__main__':
    main_handler()
