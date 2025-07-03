
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



def get_elb_cert(elb_name):
    elb=boto3.client('elb')
    response = elb.describe_load_balancers(LoadBalancerNames=[elb_name])
    listeners=response['LoadBalancerDescriptions'][0]['ListenerDescriptions']
    for listener in listeners:
        try:
            print(listener['Listener']['SSLCertificateId'])
        except KeyError:
            continue

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


print(f'ELB,CERTIFICATE')
elbs = get_lb()
for elb in elbs:
    print(f'{elb},{get_elb_cert(elb)}')

albs = get_alb()
for alb in albs:
    print(f'{alb},{get_alb_cert(alb)}')
