import os
import csv
import json
from datetime import datetime
import boto3
import time
from botocore.exceptions import ClientError
import logging

REGION='ap-south-1'


r53=boto3.client('route53', region_name=REGION)
def get_r53_hosted_zone(nextzone=None):
    if nextzone:
        response=r53.list_hosted_zones_by_name(DNSName=nextzone[0],HostedZoneId=nextzone[1])
    else:
        response=r53.list_hosted_zones_by_name()
    hosted_zone=response['HostedZones']
    if(response['IsTruncated']):
        hosted_zone += get_r53_hosted_zone((response['NextDNSName'],response['NextHostedZoneId']))
    return hosted_zone

def get_r53_zone_records(zone_id,nextzone=None):
    if (nextzone):
        response=r53.list_resource_record_sets(HostedZoneId=zone_id,NextRecordName=nextzone[0],NextRecordType=nextzone[1])
    else:
        response=r53.list_resource_record_sets(HostedZoneId=zone_id)
    zone_records=response['ResourceRecordSets']
    if (response['IsTruncated']):
        zone_records += get_r53_zone_records((zone_records['NextRecordName'],zone_records['NextRecordType']))
    return zone_records

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

time_stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ",
        datetime.utcnow().utctimetuple()
    )
hosted_zones = get_r53_hosted_zone()
for zone in hosted_zones:
    zone_folder = (time_stamp + '/' + zone['Name'][:-1])
    zone_records = get_r53_zone_records(zone['Id'])
    write_zone_to_csv(zone, zone_records)
    write_zone_to_json(zone, zone_records)
