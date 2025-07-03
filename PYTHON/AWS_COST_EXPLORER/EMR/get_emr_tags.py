import boto3
from datetime import datetime
from datetime import timedelta

create_after = datetime.now() - timedelta(days=1)
client = boto3.client('emr', region_name="ap-southeast-1")
filter_tag = "billing_subunit"
filter_val = "stage"


def get_emr_ids_after_date(dt):
    ids = []
    response = client.list_clusters(CreatedAfter=dt)['Clusters']
    for i in response:
        ids.append(i["Id"])
    return ids


def get_emr_tag_values(id):
    response = client.describe_cluster(ClusterId=id)['Cluster']['Tags']
    if len(response) == 0:
        return False
    else:
        return response


IDS = get_emr_ids_after_date(create_after)
print(IDS)
for id in IDS:
    if get_emr_tag_values(id):
        tags = get_emr_tag_values(id)
        print(tags)
        for tag in tags:
            if tag['Key'] == filter_tag and filter_val in tag["Value"]:
                print(tag["Value"])
