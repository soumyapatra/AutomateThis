import json
import logging
import os
import time
import boto3

ALERT_SNS_ARN = os.environ['ALERT_SNS_ARN']
ec2_client = boto3.client('ec2')


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    reponse = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return reponse


def enable_detailed_monitor(inst_id_list):
    response = ec2_client.monitor_instances(InstanceIds=inst_id_list)
    return response


def lambda_handler(event, context):
    try:
        if "errorCode" in event["detail"]:
            err_code = event["detail"]["errorCode"]
            err_desc = event["detail"]["errorMessage"]
            print(event["detail"]["errorMessage"])
            subject = f'Error While activating Detailed Monitoring.'
            message = f'ErrorCode: {err_code}\n\nErrorDescription: {err_desc}'
            pub_sns(ALERT_SNS_ARN, message, subject)
            return

        time.sleep(5)

        print(json.dumps(event))

        logging.info(json.dumps(event))
        monitoring_status = event['detail']['requestParameters']['monitoring']['enabled']
        message = event["detail"]["responseElements"]["instancesSet"]["items"]

        if monitoring_status is False:
            inst_ids = []

            for i in range(0, len(message)):
                inst_ids.append(message[i]['instanceId'])
            print(f'Enabling Monitoring for {inst_ids}')

            enable_detailed_monitor(inst_ids)
    except Exception as e:
        logging.info("Error:", e)
        subject = f'Error While activating Detailed Monitoring.'
        message = f'{e}'
        pub_sns(ALERT_SNS_ARN, message, subject)
