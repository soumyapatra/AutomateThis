"""
Script to List Expired Certificate in ELB and ALB
"""
from datetime import datetime
import pytz
import boto3

today = datetime.now(pytz.utc)


def get_alb_cert():
    """function for getting expired alb cert"""
    acm = boto3.client('acm')
    exp_cert_arn = []
    response = acm.list_certificates(CertificateStatuses=['EXPIRED'])
    for certificate in response['CertificateSummaryList']:
        exp_cert_arn.append(certificate['CertificateArn'])
    return exp_cert_arn


def get_elb_cert():
    """function for getting expired ELB cert"""
    iam = boto3.client('iam')
    response = iam.list_server_certificates()
    exp_cert_arn = []
    certificates = response['ServerCertificateMetadataList']
    for certificate in certificates:
        expiry = certificate['Expiration']
        if expiry < today:
            exp_cert_arn.append(certificate['Arn'])
    return exp_cert_arn


alb_cert = get_alb_cert()
elb_cert = get_elb_cert()

print(alb_cert)
print(elb_cert)
