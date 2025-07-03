import boto3


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return response
