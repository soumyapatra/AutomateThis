import boto3
def get_snap_id(ami_id):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_images(ImageIds=[ami_id])
        snap_id = []
        for device in response['Images'][0]['BlockDeviceMappings']:
            snap_id.append(device['Ebs']['SnapshotId'])
        return snap_id
    except:
        return "Not done"


def dereg_img(ami_id):
    ec2 = boto3.client('ec2')
    response = ec2.deregister_image(ImageId=ami_id)
    return response

def del_snp(snapshot_id):
    ec2 = boto3.client('ec2')
    response = ec2.delete_snapshot(SnapshotId=snapshot_id)
    return response

fh = open("ami_list.txt")

with open("ami_list.txt", 'r') as fh:
    for line in fh:
        line = line.rstrip("\n")
        snapshots = get_snap_id(line)
        print(line)
        print(dereg_img(line))
        for snapshot in snapshots:
            print(snapshot)
            print(del_snp(snapshot))
