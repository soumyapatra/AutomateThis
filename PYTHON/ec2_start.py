import boto3

ec2=boto3.client('ec2')

def ec2start(x):
    response=ec2.start_instances(InstanceIds=[x])
    return response


import boto3
sns = boto3.client('sns')

def pub_sns(arn,msg):
    response = sns.publish(
        TargetArn = arn,
        Message = msg,
    )
    print(response)

msg="EC2 Started: LOGS ---->> {}".format(ec2start('i-05c70ec9034456b5b'))

pub_sns('arn:aws:REDACTED',msg)
