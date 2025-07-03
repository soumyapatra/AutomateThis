import boto3



functions = []
client = boto3.client('lambda')
response = client.list_functions(MaxItems=100)

functions.extend(response['Functions'])

while 'NextMarker' in response:
    response = client.list_functions(Marker=response['NextMarker'],MaxItems=100)
    functions.extend(response['Functions'])

for func in functions:
    print(func['FunctionName'])
