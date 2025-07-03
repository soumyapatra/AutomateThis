
import boto3
import os
import json

def get_lb():
    elb=boto3.client('elb')
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

def get_cert(elb_name):
    elb=boto3.client('elb')
    response = elb.describe_load_balancers(LoadBalancerNames=[elb_name])
#print(response['LoadBalancerDescriptions'][0]['ListenerDescriptions']['SSLCertificateId'])

    listeners=response['LoadBalancerDescriptions'][0]['ListenerDescriptions']
    for listener in listeners:
        try:
            print(listener['Listener']['SSLCertificateId'])
        except KeyError:
            continue

elbs = get_lb()

for elb in elbs:
    print(elb)
    get_cert(elb)
