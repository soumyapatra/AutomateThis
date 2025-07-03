import boto3


r53=boto3.client('route53')

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
        response=r53.list_resource_record_sets(HostedZoneId=zone_id,StartRecordName=nextzone[0],StartRecordType=nextzone[1])
    else:
        response=r53.list_resource_record_sets(HostedZoneId=zone_id)
    zone_records=response['ResourceRecordSets']
    if (response['IsTruncated']):
        zone_records += get_r53_zone_records(zone_id,(response['NextRecordName'],response['NextRecordType']))
    return zone_records



zones=get_r53_hosted_zone()
for zone in zones:
    print(zone['Id'],zone['Name'])

zone_record=get_r53_zone_records('/hostedzone/Z1K7LK15LDI9XN')
print(zone_record)
