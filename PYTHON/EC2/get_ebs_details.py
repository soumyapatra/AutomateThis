import boto3

client = boto3.client('ec2', region_name="ap-southeast-1")


def delete_vol(id):
    response = client.delete_volume(VolumeId=id, DryRun=True)
    return response


def get_vol(tag_key, tag_val):
    total_size = 0
    count = 0
    resp = []
    response = client.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}, {'Name': f"tag:{tag_key}", 'Values': [tag_val]}])
    resp.extend(response["Volumes"])
    while "NextToken" in response:
        response = client.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}, {'Name': f"tag:{tag_key}", 'Values': [tag_val]}],
            NextToken=response["NextToken"])
        resp.extend(response["Volumes"])

    for vol in resp:
        id = vol["VolumeId"]
        size = vol["Size"]
        total_size += size
        count += 1
        print(id)
        print(delete_vol(id))
    return f"total_size: {total_size}\ncount: {count}"


print(get_vol("jenkins_server_url", "https://ci.rummycircle.com/"))
