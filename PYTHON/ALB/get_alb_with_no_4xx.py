import boto3

def get_alb(region):
    alb = boto3.client('elbv2', region_name=region)
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancers"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        name = lb["LoadBalancerArn"]
        lb_arn = name.split(':')[-1]
        lb_arn = lb_arn.replace('loadbalancer/', '')
        alb_names.append(lb_arn)
    return alb_names


def get_alarm_names(region, alb):
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if alarm['MetricName'] == "HTTPCode_Target_4XX_Count":
            for dimension in alarm['Dimensions']:
                if dimension['Name'] == "LoadBalancer":
                    if dimension['Value'] in alb:
                        alb.remove(dimension['Value'])

REGION = "ap-south-1"

if __name__ == "__main__":
    alb = get_alb(REGION)
    print("ALB: ", len(alb))
    print(alb, "\n", "ALB: ", len(alb))