import boto3
import json
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DOCUMENT_NAME = os.environ['DOCUMENT_NAME']
SNSTARGET = os.environ['SNSTARGET']
REGION = os.environ['REGION']

ssm_client = boto3.client('ssm',region_name=REGION)


def abandon_lifecycle(life_cycle_hook, auto_scaling_group, instance_id):
    asg_client = boto3.client('autoscaling')
    try:
        response = asg_client.complete_lifecycle_action(
            LifecycleHookName=life_cycle_hook,
            AutoScalingGroupName=auto_scaling_group,
            LifecycleActionResult='ABANDON',
            InstanceId=instance_id
        )
        if check_response(response):
            logger.info("Lifecycle hook abandoned correctly: %s", response)
        else:
            logger.error("Lifecycle hook could not be abandoned: %s", response)
    except Exception as e:
        logger.error("Lifecycle hook abandon could not be executed: %s", str(e))
        return None


def get_inst_tag(inst_id, tag_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
    tags = response['Tags']
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return None


def check_command(command_id, instance_id):
    timewait = 1
    while True:
        time.sleep(10)
        response_iterator = ssm_client.list_command_invocations(
            CommandId=command_id,
            InstanceId=instance_id,
            Details=False
        )
        logging.info("list command invoations: %s", response_iterator)

        if check_response(response_iterator):
            response_iterator_status = response_iterator['CommandInvocations'][0]['Status']
            if response_iterator_status != 'Pending':
                if response_iterator_status == "Success":
                    return True
                elif response_iterator_status == 'InProgress':
                    logging.info("Status: %s", response_iterator_status)
                elif response_iterator_status == 'Failed':
                    logging.error("ERROR: status: %s", response_iterator)
                    return False
        time.sleep(timewait)
        timewait += timewait


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
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName=DOCUMENT_NAME,
            Parameters={
                'ASGNAME': [asg_name],
                'LIFECYCLEHOOKNAME': [hook_name],
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


def backup_dir(inst_id):
    app_tag = get_inst_tag(inst_id,"app_name")
    if app_tag is not None:
        return f'/home/deploy/{app_tag}/logs'
    else:
        return False


def list_document(doc_name):
    document_filter_parameters = {'key': 'Name', 'value': doc_name}
    response = ssm_client.list_documents(
        DocumentFilterList=[document_filter_parameters]
    )
    return response


def check_document(doc_name):
    # If the document already exists, it will not create it.
    try:
        response = list_document(doc_name)
        if check_response(response):
            logger.info("Documents list: %s", response)
            if response['DocumentIdentifiers']:
                logger.info("Documents exists: %s", response)
                return True
            else:
                return False
        else:
            logger.error("Documents' list error: %s", response)
            return False
    except Exception as e:
        logger.error("Document error: %s", str(e))
        return None


def lambda_handler(event, context):
    try:
        print(json.dumps(event))
        detail = event['detail']
        if "LifecycleHookName" in detail and "AutoScalingGroupName" in detail:
            hook_name = detail['LifecycleHookName']
            print(hook_name)
            asg_name = detail['AutoScalingGroupName']
            print(asg_name)
            instance_id = detail['EC2InstanceId']
            print(instance_id)
            if check_document(DOCUMENT_NAME):
                command_id = send_command(instance_id, hook_name, asg_name, DOCUMENT_NAME)
                print(command_id)
                if command_id is not None:
                    if check_command(command_id, instance_id):
                        print("LAMBDA executed successfully")
                    else:
                        print("Command Issue, Abondoning")
                        abandon_lifecycle(hook_name, asg_name, instance_id)
                else:
                    abandon_lifecycle(hook_name, asg_name, instance_id)
            else:
                print("Document does not exist, Abondoning")
                abandon_lifecycle(hook_name, asg_name, instance_id)
    except Exception as e:
        logging.error("Error: %s", str(e))
