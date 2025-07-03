import boto3

REGION="ap-southeast-1"

def get_lb():
    elb=boto3.client('elb',region_name=REGION)
    response=elb.describe_load_balancers()
    lbs=[]
    elb_names=[]
    lbs.extend(response["LoadBalancerDescriptions"])
    if 'NextMarker' in response:
        response = elb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancerDescriptions"])
    for lb in lbs:
        elb_names.append(lb["LoadBalancerName"])
    return elb_names

def get_elb_log(elb_name):
    elb=boto3.client('elb',region_name=REGION)
    response=elb.describe_load_balancer_attributes(LoadBalancerName=elb_name)
    return response['LoadBalancerAttributes']['AccessLog']['Enabled']
    #if response['LoadBalancerAttributes']['AccessLog']['Enabled'] == False:
    #    return
    #else:
    #    return True

lbs=get_lb()
for lb in lbs:
    print(lb,get_elb_log(lb))
