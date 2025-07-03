import os
import csv
import json
from datetime import datetime
import boto3
import time
from botocore.exceptions import ClientError
import logging

S3_BUCKET = os.environ['S3_BUCKET']
SNS = os.environ['SNS']
REGION = os.environ['REGION']

s3 = boto3.resource('s3')
r53 = boto3.client('route53',region_name=REGION)


def upload_to_s3(folder, filename, bucket_name, key):
    """Upload a file to a folder in an Amazon S3 bucket."""
    key = f'route53-backup/{folder}/{key}'
    print(key)
    s3.meta.client.upload_file(filename, bucket_name, key)


def get_r53_hosted_zone(nextzone=None):
    try:
        if nextzone:
            response = r53.list_hosted_zones_by_name(DNSName=nextzone[0], HostedZoneId=nextzone[1])
        else:
            response = r53.list_hosted_zones_by_name()
        hosted_zone = response['HostedZones']
        if (response['IsTruncated']):
            hosted_zone += get_r53_hosted_zone((response['NextDNSName'], response['NextHostedZoneId']))
        return hosted_zone
    except Exception as e:
        logging.error("route53 get host zone failed:", e)


def get_r53_zone_records(zone_id, nextzone=None):
    try:

        if (nextzone):
            response = r53.list_resource_record_sets(HostedZoneId=zone_id, StartRecordName=nextzone[0],
                                                     StartRecordType=nextzone[1])
        else:
            response = r53.list_resource_record_sets(HostedZoneId=zone_id)
        zone_records = response['ResourceRecordSets']
        if (response['IsTruncated']):
            zone_records += get_r53_zone_records(zone_id, (response['NextRecordName'], response['NextRecordType']))
        return zone_records
    except Exception as e:
        logging.error("route53 record issue:", e)


def get_record_value(record):
    """Return a list of values for a hosted zone record."""
    # test if record's value is Alias or dict of records
    try:
        value = [':'.join(
            ['ALIAS', record['AliasTarget']['HostedZoneId'],
             record['AliasTarget']['DNSName']]
        )]
    except KeyError:
        value = []
        for v in record['ResourceRecords']:
            value.append(v['Value'])
    return value


def try_record(test, record):
    """Return a value for a record"""
    # test for Key and Type errors
    try:
        value = record[test]
    except KeyError:
        value = ''
    except TypeError:
        value = ''
    return value


def write_zone_to_csv(zone, zone_records):
    """Write hosted zone records to a csv file in /tmp/."""
    zone_file_name = '/tmp/' + zone['Name'] + 'csv'
    # write to csv file with zone name
    with open(zone_file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # write column headers
        writer.writerow([
            'NAME', 'TYPE', 'VALUE',
            'TTL', 'REGION', 'WEIGHT',
            'SETID', 'FAILOVER', 'EVALUATE_HEALTH'
        ])
        # loop through all the records for a given zone
        for record in zone_records:
            csv_row = [''] * 9
            csv_row[0] = record['Name']
            csv_row[1] = record['Type']
            csv_row[3] = try_record('TTL', record)
            csv_row[4] = try_record('Region', record)
            csv_row[5] = try_record('Weight', record)
            csv_row[6] = try_record('SetIdentifier', record)
            csv_row[7] = try_record('Failover', record)
            csv_row[8] = try_record('EvaluateTargetHealth',
                                    try_record('AliasTarget', record)
                                    )
            value = get_record_value(record)
            # if multiple values (e.g., MX records), write each as its own row
            for v in value:
                csv_row[2] = v
                writer.writerow(csv_row)
    return zone_file_name


def write_zone_to_json(zone, zone_records):
    """Write hosted zone records to a json file in /tmp/."""
    zone_file_name = '/tmp/' + zone['Name'] + 'json'
    # write to json file with zone name
    with open(zone_file_name, 'w') as json_file:
        json.dump(zone_records, json_file, indent=4)
    return zone_file_name


def pub_sns(arn, msg):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn=arn,
        Message=msg,
    )
    return response


def getR53Backup():
    try:
        time_stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                   datetime.utcnow().utctimetuple()
                                   )
        hosted_zones = get_r53_hosted_zone()
        for zone in hosted_zones:
            zone_folder = (time_stamp + '/' + zone['Name'][:-1])
            zone_records = get_r53_zone_records(zone['Id'])
            print(zone_folder, write_zone_to_csv(zone, zone_records), S3_BUCKET, zone['Name'] + 'csv')
            upload_to_s3(zone_folder, write_zone_to_csv(zone, zone_records), S3_BUCKET, zone['Name'] + 'csv')
            upload_to_s3(zone_folder, write_zone_to_json(zone, zone_records), S3_BUCKET, zone['Name'] + 'json')
            logging.info("Backup Completed")
        return True
    except Exception as e:
        logging.error("Failed:", e)
        return False


def lambda_handler(event, context):
    result = getR53Backup()
    if result is True:
        logging.info("Backup Completed")
    else:
        pub_sns(SNS, "Route53 Backup Failed. Check Cloudwatch Logs for more info.")
