import boto3

def get_acct_id():
    sts=boto3.client('sts')
    return sts.get_caller_identity()
acct_id=get_acct_id()
print(acct_id)
