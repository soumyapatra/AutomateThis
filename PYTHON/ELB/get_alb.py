import boto3


def get_alb():
    alb = boto3.client('elbv2')
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancers"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        alb_names.append(lb["LoadBalancerArn"])
    return alb_names

#print(get_alb())

def get_alb_cert(alb_name):
    elb=boto3.client('elbv2')
    response = elb.describe_listeners(LoadBalancerArn=alb_name)
    listeners=response['Listeners']
    for listener in listeners:
        try:
            certificates = listener['Certificates']
            for certificate in certificates:
                print(certificate['CertificateArn'])
        except KeyError:
            continue
albs = get_alb()
for alb in albs:
    data = alb, get_alb_cert(alb)
    print(data)
#get_alb_cert('arn:aws:REDACTED')
