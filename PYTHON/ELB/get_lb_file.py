
import boto3
import os
import json
import csv
from datetime import datetime
from datetime import date


FILE = f'/tmp/lb_details_{date.today()}'

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
            print("NA")

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
            print("NA")


col_head="LB,certificates\n"
col_write=open(FILE,"w")
col_write.write(col_head)
col_write.close()


elbs = get_lb()
with open(FILE, "a") as csvFile:
    for elb in elbs:
        get_elb_cert(elb)
        parsed_data = get_elb_cert(elb)
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(parsed_data)


albs = get_alb()
with open(FILE, "a") as csvFile:
    for alb in albs:
        get_alb_cert(alb)
        parsed_data = get_alb_cert(alb)
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(parsed_data)


