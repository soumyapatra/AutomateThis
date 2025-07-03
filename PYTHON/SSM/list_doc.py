import boto3
import logging

ssm=boto3.client('ssm')

reponse=ssm.list_documents()
doc_list=[]
doc_list.extend(reponse['DocumentIdentifiers'])
while 'NextToken' in reponse:
    reponse=ssm.list_documents(NextToken=reponse['NextToken'])
    doc_list.extend(reponse['DocumentIdentifiers'])

for doc in doc_list:
    if doc['Name'] == 'InstallCwAgent':
        print('present')
