import boto3
import pandas as pd

session = boto3.Session()
ec2 = session.client('ec2')

volumes = ec2.describe_volumes()

volume_data = []
for volume in volumes['Volumes']:
    volume_id = volume['VolumeId']
    name_tag = None
    if 'Tags' in volume:
        for tag in volume['Tags']:
            if tag['Key'] == 'Name':
                name_tag = tag['Value']
                break
    volume_data.append({'VolumeId': volume_id, 'Name': name_tag})

df = pd.DataFrame(volume_data)

df.to_csv('volumes.csv', index=False)

print("Volume information has been saved to volumes.csv")
