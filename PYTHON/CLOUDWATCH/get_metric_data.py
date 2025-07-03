import boto3
from datetime import datetime
from datetime import timedelta

cw = boto3.client('cloudwatch')


def get_cpu_metric(inst_id):
    response = cw.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
        ],
        StartTime=datetime.now() - timedelta(minutes=5),
        EndTime=datetime.now(),
        Period=300,
        Statistics=['Average'],
    )
    print(response)


get_cpu_metric("i-0cb022e14f77fa34d")
