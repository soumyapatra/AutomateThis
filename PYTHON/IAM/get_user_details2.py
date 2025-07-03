import boto3
import csv

iam=boto3.client('iam')
FILE="/tmp/iam.csv"
paginator = iam.get_paginator('get_account_authorization_details')

pages = paginator.paginate(Filter=['User'])

col_head="Username,PolicyName,GroupList\n"
col_write=open(FILE,'w')
col_write.write(col_head)
col_write.close()


for page in pages:
    for users in page['UserDetailList']:
        for i in range(0,len(users['AttachedManagedPolicies'])):
            with open(FILE,"a") as csvFile:
                parsed_data=users['UserName'],users["AttachedManagedPolicies"][i]['PolicyName'],users['GroupList']
                csvWriter=csv.writer(csvFile)
                csvWriter.writerow(parsed_data)
