import boto3

REGION = "ap-south-1"
FILENAME = "./lists.txt"
ZONE_ID = "Z2IDUVEAUM83TO"

client = boto3.client("route53", region_name=REGION)


def change_r53_record(zone_id, dns_name, ip):
    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Comment': 'Changing resource record using boto3',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': dns_name,
                        'Type': 'A',
                        'TTL': 30,
                        'ResourceRecords': [
                            {
                                'Value': ip
                            },
                        ]
                    }
                },
            ]
        }
    )
    return response


def get_r53_records(zone_id, dns_name):
    response = client.list_resource_record_sets(
        HostedZoneId=zone_id,
        StartRecordName=dns_name,
        StartRecordType='A',
        MaxItems="1"
    )
    try:
        record_set_name = response["ResourceRecordSets"][0]["Name"]
        if record_set_name != f"{dns_name}.":
            return True
        else:
            return False
    except Exception as e:
        print("Issue: ", e)


file1 = open(FILENAME, 'r')
lines = file1.read().splitlines()

for line in lines:
    ip = line.split()[0]
    dns_name = line.split()[1]
    if get_r53_records(ZONE_ID, dns_name):
        print(ip, dns_name)
        print(change_r53_record(ZONE_ID, dns_name, ip))
