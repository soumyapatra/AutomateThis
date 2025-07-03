import boto3
import os
import json
import csv
from datetime import datetime
from datetime import date




regions=["ap-south-1","ap-southeast-1"]

def get_lb(region):
    elb=boto3.client('elb',region_name=region)
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



def get_elb_cert(elb_name,region):
    elb=boto3.client('elb',region_name=region)
    elb_cert=[]
    response = elb.describe_load_balancers(LoadBalancerNames=[elb_name])
    listeners=response['LoadBalancerDescriptions'][0]['ListenerDescriptions']
    for listener in listeners:
        if "SSLCertificateId" in listener['Listener']:
             elb_cert.append(listener['Listener']['SSLCertificateId'])
    return elb_cert




def get_alb(region):
    alb = boto3.client('elbv2',region_name=region)
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




def get_alb_cert(alb_name,region):
    elb=boto3.client('elbv2',region_name=region)
    alb_cert = []
    response = elb.describe_listeners(LoadBalancerArn=alb_name)
    listeners=response['Listeners']
    for listener in listeners:
        if "Certificates" in listener:
            certificates = listener['Certificates']
            for certificate in certificates:
                alb_cert.append(certificate['CertificateArn'])
    return alb_cert



for region in regions:
    ELB_FILE = f'/tmp/elb_details_{region}_{date.today()}.csv'
    ALB_FILE = f'/tmp/alb_details_{region}_{date.today()}.csv'
    col_head = "LB,certificates\n"
    col_write = open(ELB_FILE, "w")
    col_write.write(col_head)
    col_write.close()
    elbs = get_lb(region)
    with open(ELB_FILE, "a") as elb_file:
        for elb in elbs:
            certs = get_elb_cert(elb,region)
            if certs == []:
                continue
            data = f'{elb},{", ".join(certs)}\n'
            elb_file.write(data)

    col_head = "ALB_ARN,certificates\n"
    col_write = open(ALB_FILE, "w")
    col_write.write(col_head)
    col_write.close()
    albs = get_alb(region)
    with open(ALB_FILE, "a") as alb_file:
        for alb in albs:
            certs = get_alb_cert(alb,region)
            if certs == []:
                continue
            data = f'{alb},{", ".join(certs)}\n'
            alb_file.write(data)






