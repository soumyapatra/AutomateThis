import boto3


def get_dist_log(id, region):
    cf_client = boto3.client("cloudfront", region_name=region)
    response = cf_client.get_distribution(Id=id)["Distribution"]["DistributionConfig"]
    if response["Logging"]["Enabled"]:
        bucket = response["Logging"]["Bucket"].replace(".s3.amazonaws.com", "")
        prefix = response["Logging"]["Prefix"]
        return f'{bucket}/{prefix}'
    else:
        return False


def get_dist_id(region):
    cf_client = boto3.client("cloudfront", region_name=region)
    cf_list = []
    id_list = []
    response = cf_client.list_distributions()['DistributionList']
    cf_list.extend(response["Items"])
    if "NextMarker" in response:
        cf_list.extend(response["Items"])
    for item in cf_list:
        id_list.append(item['Id'])
    return id_list


ids = get_dist_id("ap-southeast-1")
for id in ids:
    if get_dist_log(id, "ap-southeast-1"):
        print(id, get_dist_log(id, "ap-southeast-1"))
