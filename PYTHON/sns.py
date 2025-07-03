import boto3
sns = boto3.client('sns')
list=["Test","Message"]
list1=["LAST","test","Message"]
def pub_sns(arn,msg):
    reponse = sns.publish(
        TargetArn = arn,
        Message = msg,
    )
    print(reponse)
msg=f'the list includes the following\n{list}\nanother line with some text\ntestmessage\nlast list {list1}'
pub_sns('arn:aws:REDACTED',msg)
