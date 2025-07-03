import boto3
import json
lamb=boto3.client('lambda')
payload={'msg':'hi there'}
response=lamb.invoke(FunctionName='json_test',InvocationType='Event',Payload=json.dumps(payload))
print(response)
