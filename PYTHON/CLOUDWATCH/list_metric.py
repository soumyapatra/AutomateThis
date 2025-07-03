import boto3

cw = boto3.client('cloudwatch')

metrics = []
response = cw.list_metrics(Namespace='AWS/Logs', MetricName='IncomingBytes')
metrics.extend(response['Metrics'])
while 'NextToken' in response:
    response = cw.list_metrics(Namespace='AWS/Logs', MetricName='IncomingBytes', NextToken=response['NextToken'])
    metrics.extend(response)
print(metrics)
