import boto3

ec2=boto3.client('ec2')
images = ec2.describe_images(Owners=['self'],Filters=[{'Name':'name','Values':['ami_backup_10.14.25.132']}])
asg=boto3.client('autoscaling',region_name='ap-south-1')


asgs=asg.describe_auto_scaling_groups()
for asgnames in asgs['AutoScalingGroups']:
    for sus_proc in asgnames['SuspendedProcesses']:
        if sus_proc['ProcessName'] == "Launch" or sus_proc['ProcessName'] == "Terminate":
            print(asgnames['AutoScalingGroupName'],"",sus_proc)
