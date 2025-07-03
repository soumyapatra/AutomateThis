import boto3
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

S3BUCKET = "stage.xxxxxxxx.sonartest"
SNSTARGET = "AWS-ARN"
DOC_NAME = "asg-sns-4"


ssm_client = boto3.client('ssm')


def get_inst_tag(inst_id, tag_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
    tags = response['Tags']
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return None


def backup_dir(inst_id):
    app_tag = get_inst_tag(inst_id, "app_name")
    if app_tag is not None:
        return f'/home/deploy/{app_tag}/logs'
    else:
        return False


def send_command(instance_id, hook_name, asg_name, doc_name):
    # Until the document is not ready, waits in accordance to a backoff mechanism.
    while True:
        timewait = 1
        response = list_document(doc_name)
        if any(response["DocumentIdentifiers"]):
            break
        time.sleep(timewait)
        timewait += timewait
    try:
        BACKUPDIRECTORY = backup_dir(instance_id)
        APPNAME = get_inst_tag(instance_id, "app_name")
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName=doc_name,
            Parameters={
                'ASGNAME': [asg_name],
                'LIFECYCLEHOOKNAME': [hook_name],
                'BACKUPDIRECTORY': [BACKUPDIRECTORY],
                'S3BUCKET': [S3BUCKET],
                'APPNAME': [APPNAME],
                'SNSTARGET': [SNSTARGET]},
            TimeoutSeconds=600
        )
        if check_response(response):
            logger.info("Command sent: %s", response)
            print(response['Command']['CommandId'])
            return response['Command']['CommandId']
        else:
            logger.error("Command could not be sent: %s", response)
            return None
    except Exception as e:
        logger.error("Command could not be sent: %s", str(e))
        return None


def check_response(response_json):
    try:
        if response_json['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except KeyError:
        return False


def list_document(doc_name):
    document_filter_parameters = {'key': 'Name', 'value': doc_name}
    response = ssm_client.list_documents(
        DocumentFilterList=[document_filter_parameters]
    )
    return response


send_command("i-04391becc7443a3d9","test1","terraform-nodejs-asg",DOC_NAME)
