import boto3

iam=boto3.client('iam')

paginator = iam.get_paginator('get_account_authorization_details')

pages = paginator.paginate(Filter=['User'])
for page in pages:
    for users in page['UserDetailList']:
        for i in range(0,len(users['AttachedManagedPolicies'])):
            print(users['UserName'],users['AttachedManagedPolicies'][i]['PolicyName'],users['GroupList'])
