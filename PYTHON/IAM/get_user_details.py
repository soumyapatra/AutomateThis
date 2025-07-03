import boto3


iam=boto3.client('iam')
users=[]

response=iam.get_account_authorization_details(Filter=['User'])
users.extend(response['UserDetailList'])


while response['IsTruncated'] == "True":
    response=iam.get_account_authorization_details(Filter=['User'],Marker=response['Marker'])
    users.extend(response['UserDetailList'])

for user in users:
    print(user['UserName'],user['GroupList'],user['AttachedManagedPolicies'])
