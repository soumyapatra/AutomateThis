


import boto3
s3 = boto3.resource('s3')
s3.meta.client.download_file('xxxxxxxx.prod-app-logs', 'applications/auditservice/10.200.3.227/logs/auditservice.2020-02-08.0.log.gz', 'auditservice.2020-02-08.0.log.gz')