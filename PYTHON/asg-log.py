import boto3
import json
import logging
import time
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ssm_client = boto3.client("ssm")

LIFECYCLE_KEY = "LifecycleHookName"
ASG_KEY = "AutoScalingGroupName"
EC2_KEY = "EC2InstanceId"
RESPONSE_DOCUMENT_KEY = "DocumentIdentifiers"

ASGNAME = os.environ['ASGNAME']
S3BUCKET = os.environ['S3BUCKET']
SNSTARGET = os.environ['SNSTARGET']
DOCUMENT_NAME = os.environ['SSM_DOCUMENT_NAME']
APPNAME = os.environ['APPNAME']
EC2ID = os.environ['EC2ID']



def backup_dir(ASGNAME):
    auto_scaling_group = ASGNAME
    print(auto_scaling_group)
    if auto_scaling_group == 'asgname-1':
        return "/opt/backup/logs/"
    else:
        return "/opt/tomcat-nfs/logs"



# CHECK RESPONSE

def check_response(response_json):
    try:
        if response_json['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except KeyError:
        return False


# LIST DOCUMENT

def list_document():
    document_filter_parameters = {'key': 'Name', 'value': DOCUMENT_NAME}
    response = ssm_client.list_documents(
        DocumentFilterList=[document_filter_parameters]
    )
    return response


def check_document():
    # If the document already exists, it will not create it.
    try:
        response = list_document()
        if check_response(response):
            logger.info("Documents list: %s", response)
            if response[RESPONSE_DOCUMENT_KEY]:
                logger.info("Documents exists: %s", response)
                return True
            else:
                return False
        else:
            logger.error("Documents' list error: %s", response)
            return False
    except Exception, e:
        logger.error("Document error: %s", str(e))
        return None


def send_command(instance_id):
    # Until the document is not ready, waits in accordance to a backoff mechanism.
    while True:
        timewait = 1
        response = list_document()
        if any(response[RESPONSE_DOCUMENT_KEY]):
            break
        time.sleep(timewait)
        timewait += timewait
    try:
        BACKUPDIRECTORY = backup_dir(ASGNAME)
        response = ssm_client.send_command(
            InstanceIds = [ 'i-040fffbf8b9568e91' ],
            DocumentName=DOCUMENT_NAME,
            Parameters={
		'ASGNAME': [ASGNAME],
                'BACKUPDIRECTORY': [BACKUPDIRECTORY],
                'S3BUCKET': [S3BUCKET],
                'APPNAME': [APPNAME],
                'SNSTARGET': [SNSTARGET]},
            TimeoutSeconds=600
        )
        if check_response(response):
            logger.info("Command sent: %s", response)
            print response['Command']['CommandId']
            return response['Command']['CommandId']
        else:
            logger.error("Command could not be sent: %s", response)
            return None
    except Exception, e:
        logger.error("Command could not be sent: %s", str(e))
        return None

def check_command(command_id, instance_id):
    timewait = 1
    while True:
        response_iterator = ssm_client.list_command_invocations(
            CommandId = command_id,
            InstanceId = 'i-040fffbf8b9568e91',
            Details=False
            )
        if check_response(response_iterator):
            response_iterator_status = response_iterator['CommandInvocations'][0]['Status']
      	    print (response_iterator_status)
            if response_iterator_status != 'Pending':
                if response_iterator_status == 'InProgress' or response_iterator_status == 'Success':
                    logging.info( "Status: %s", response_iterator_status)
                    return True
                else:
                    logging.error("ERROR: status: %s", response_iterator)
                    return False
        time.sleep(timewait)
        timewait += timewait


def lambda_handler():
    try:
        instance_id = [EC2ID]
        if check_document():
            logging.info("Document Present")
            send_command(instance_id)
        else:
            logging.info("Document Not Present")
    except Exception, e:
        logging.error("Error: %s", str(e))

lambda_handler()
