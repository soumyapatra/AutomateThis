import boto3

cw=boto3.client('cloudwatch')
alb=boto3.client('elbv2')

response_alb=alb.describe_load_balancers(PageSize=100)
lbs=[]
lbs.extend(response_alb["LoadBalancers"])
lb_arns=[]
while "NextMarker" in response_alb:
    response_alb = alb.describe_load_balancers(Marker=response_alb["NextMarker"],PageSize=100)
    lbs.extend(response_alb["LoadBalancers"])
for lb in lbs:
    lb_arns.append(lb["LoadBalancerArn"].split(':')[-1].replace('loadbalancer/',''))
#print(lb_arns)


response_cw=cw.describe_alarms(StateValue='INSUFFICIENT_DATA',MaxRecords=100)
alarms=[]
alarms.extend(response_cw['MetricAlarms'])
while 'NextToken' in response_cw:
    response_cw = cw.describe_alarms(StateValue='INSUFFICIENT_DATA',NextToken=response_cw['NextToken'],MaxRecords=100)
    alarms.extend(response_cw["MetricAlarms"])
cw_alb=[]
for alarm in alarms:
    for dimension in alarm["Dimensions"]:
        if dimension["Name"] == "LoadBalancer":
            cw_alb.append(dimension["Value"])

for alb in cw_alb:
    if alb not in lb_arns:
        print(f'Deleting alarm: {alb}')
        print(cw.delete_alarms(AlarmNames=[alb]))
