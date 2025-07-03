# Import the SDK and required libraries
import boto3
import json
import os
import logging
import sys
import socket
import requests
import ssl
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure the SNS topic which you want to use for sending notifications
namespace = os.environ['NAMESPACE']
REGION = os.environ['REGION']
ACCOUNT_ID = os.environ['ACCOUNT_ID']
ondemand_healthcheck_flag = os.environ['ONDEMAND_HEALTHCHECK']
sns_arn = os.environ['SNS_TOPIC']


if namespace == 'AWS/ELB':
    tg_arn = None
    tg_type = None
else:
    tg_type = (os.environ['TARGETGROUP_TYPE'].strip()).lower()


def lambda_handler(event, context):
    print(json.dumps(event))
    msg = json.loads(event['Records'][0]['Sns']['Message'])
    print(msg)

    """
	Main Lambda handler
	"""
    print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    global sns_client
    global elb_client
    global elbv2_client
    global ec2_client

    try:
        sns_client = boto3.client('sns')
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

    try:
        elb_client = boto3.client('elb')
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

    try:
        elbv2_client = boto3.client('elbv2')
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

    try:
        ec2_client = boto3.client('ec2')
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

    if "AlarmName" in message:
        json_message = json.loads(message)
        accountid = str(json_message['AWSAccountId'])
        alarm_trigger = str(json_message['NewStateValue'])
        timestamp = str(json_message['StateChangeTime'])
        region = os.environ["AWS_REGION"]
        logger.info("=======Start Lambda Function=======")
        logger.info("AccountID:{}".format(accountid))
        logger.info("Region:{}".format(region))
        logger.info("Namespace:{}".format(namespace))
        logger.info("Alarm State:{}".format(alarm_trigger))
        if namespace == "AWS/ELB":
            elb_name = str(json_message['Trigger']['Dimensions'][0]['value'])
        elif namespace == "AWS/ApplicationELB":
            for entity in json_message['Trigger']['Dimensions']:
                if entity['name'] == "LoadBalancer":
                    elb_name = str(entity['value'])
        elif namespace == "AWS/NetworkELB":
            for entity in json_message['Trigger']['Dimensions']:
                if entity['name'] == "LoadBalancer":
                    elb_name = str(entity['value'])

                # Take actions when an Alarm is triggered
        if alarm_trigger == 'ALARM':
            if namespace == "AWS/ELB":
                lbtype = 'elb'
                # Get health check port from healthcheck configuration for CLB
                unhealthy_list, unhealthy_instances_id_list = describe_instance_health(elb_name)
                if ondemand_healthcheck_flag:
                    ondemand_healthcheck_result_list = []
                    healthcheck_config = describe_elb_ondemand_healthcheck(elb_name=elb_name)
                    hc_type = healthcheck_config['HealthCheckProtocol']
                    unhealthy_instances_ip_list = get_instance_private_ip(unhealthy_instances_id_list)
                    logger.info("Health Check type:{}".format(hc_type))
                    logger.info("Health Check Config:{}".format(healthcheck_config))
                    if hc_type == 'TCP':
                        ondemand_healthcheck_result_list = ondemand_tcp_healthcheck(unhealthy_instances_ip_list,
                                                                                    healthcheck_config, lbtype)
                    elif hc_type == 'SSL':
                        ondemand_healthcheck_result_list = ondemand_ssl_healthcheck(unhealthy_instances_ip_list,
                                                                                    healthcheck_config, lbtype)
                    elif hc_type == 'HTTP' or hc_type == 'HTTPS':
                        ondemand_healthcheck_result_list = ondemand_http_https_healthcheck(unhealthy_instances_ip_list,
                                                                                           healthcheck_config, lbtype)
                    else:
                        logger.error("HealthCheck Type -- {} is not supported by AWS/ELB".format(hc_type))
                send_sns(unhealthy_list, elb_name, region, timestamp, accountid, ondemand_healthcheck_flag,
                         ondemand_healthcheck_result_list, lbtype, tg_arn)
            elif namespace == "AWS/ApplicationELB":
                dimensions = msg['Trigger']['Dimensions']
                for dimension in dimensions:
                    if dimension['name'] == "TargetGroup":
                        TG_NAME = dimension['value']
                        print(TG_NAME)
                        TG_ARN = f'arn:aws:REDACTED'
                        print(f'TG_ARN: {TG_ARN}\nTG_NAME: {TG_NAME}')
                lbtype = 'elbv2/alb'
                # Get health check port from describe target health as one target group can have different health check ports for each target
                unhealthy_list, unhealthy_targets_ip_port_list = describe_target_health(TG_ARN, elb_name, tg_type)
                if ondemand_healthcheck_flag:
                    ondemand_healthcheck_result_list = []
                    healthcheck_config = describe_targetgroup_ondemand_healthcheck(targetgroup_arn=TG_ARN)
                    hc_type = healthcheck_config['HealthCheckProtocol']
                    logger.info("Health Check type:{}".format(hc_type))
                    logger.info("Health Check Config:{}".format(healthcheck_config))
                    if hc_type == 'HTTP' or hc_type == 'HTTPS':
                        ondemand_healthcheck_result_list = ondemand_http_https_healthcheck(
                            unhealthy_targets_ip_port_list, healthcheck_config, lbtype)
                    else:
                        logger.error("HealthCheck Type -- {} is not supported by AWS/ApplicationELB".format(hc_type))
                send_sns(unhealthy_list, elb_name, region, timestamp, accountid, ondemand_healthcheck_flag,
                         ondemand_healthcheck_result_list, lbtype, TG_ARN)
            elif namespace == "AWS/NetworkELB":
                lbtype = 'elbv2/nlb'
                # Get health check port from describe target health as one target group can have different health check ports for each target
                unhealthy_list, unhealthy_targets_ip_port_list = describe_target_health(tg_arn, elb_name, tg_type)
                if ondemand_healthcheck_flag:
                    ondemand_healthcheck_result_list = []
                    healthcheck_config = describe_targetgroup_ondemand_healthcheck(targetgroup_arn=tg_arn)
                    hc_type = healthcheck_config['HealthCheckProtocol']
                    logger.info("Health Check type:{}".format(hc_type))
                    logger.info("Health Check Config:{}".format(healthcheck_config))
                    if hc_type == 'TCP':
                        ondemand_healthcheck_result_list = ondemand_tcp_healthcheck(unhealthy_targets_ip_port_list,
                                                                                    healthcheck_config, lbtype)
                    elif hc_type == 'HTTP' or hc_type == 'HTTPS':
                        ondemand_healthcheck_result_list = ondemand_http_https_healthcheck(
                            unhealthy_targets_ip_port_list, healthcheck_config, lbtype)
                    else:
                        logger.error("HealthCheck Type -- {} is not supported by AWS/NetworkELB".format(hc_type))
                send_sns(unhealthy_list, elb_name, region, timestamp, accountid, ondemand_healthcheck_flag,
                         ondemand_healthcheck_result_list, lbtype, tg_arn)


def send_sns(unhealthy_list, elb_name, region, timestamp, accountid, ondemand_healthcheck_flag,
             ondemand_healthcheck_result_list, lbtype, tg_arn):
    """
	Send notification to SNS topic subscribers of unhealthy instances/targets
	"""
    logger.info("\n==SNS notification meta data==\n")
    logger.info(
        "timestamp:{}\n accountid:{}\n region:{}\n elb_name:{}\n unhealthy_list:{}\n".format(timestamp, accountid,
                                                                                             region, elb_name,
                                                                                             unhealthy_list))
    if lbtype == 'elb':
        if ondemand_healthcheck_flag:
            message = "Account: {} \nTimestamp: {} \nRegion: {} \nELB: {}" \
                      "\nUnhealthy Targets and Cause of Failure: \n{}" \
                      "\n\nOnDemand Health Check Result: \n{}" \
                      "\n\n\nFor more information about how to troubleshoot unhealthy " \
                      "targets, please refer to the following links:" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-unhealthy-checks-ecs/" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-classic-health-checks/ \n\n\n" \
                .format(accountid, timestamp, region, elb_name, "\n".join(str(x) for x in unhealthy_list),
                        "\n".join(str(x) for x in ondemand_healthcheck_result_list))
        else:
            message = "Account: {} \nTimestamp: {} \nRegion: {} \nELB: {}" \
                      "\nUnhealthy Targets and Cause of Failure: \n{}" \
                      "\n\n\nFor more information about how to troubleshoot unhealthy " \
                      "targets, please refer to the following links:" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-unhealthy-checks-ecs/" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-classic-health-checks/ \n\n\n" \
                .format(accountid, timestamp, region, elb_name, "\n".join(str(x) for x in unhealthy_list))
    if lbtype == 'elbv2/alb' or lbtype == 'elbv2/nlb':
        if ondemand_healthcheck_flag:
            message = "Account: {} \nTimestamp: {} \nRegion: {} \nELB: {}\nTargetGroupARN: {}" \
                      "\nUnhealthy Targets and Cause of Failure: \n{}" \
                      "\n\nOnDemand Health Check Result: \n{}" \
                      "\n\n\nFor more information about how to troubleshoot unhealthy " \
                      "targets, please refer to the following links:" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-unhealthy-checks-ecs/" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-classic-health-checks/ \n\n\n" \
                .format(accountid, timestamp, region, elb_name, tg_arn, "\n".join(str(x) for x in unhealthy_list),
                        "\n".join(str(x) for x in ondemand_healthcheck_result_list))
        else:
            message = "Account: {} \nTimestamp: {} \nRegion: {} \nELB: {} \nTargetGroupARN: {}" \
                      "\nUnhealthy Targets and Cause of Failure: \n{}" \
                      "\n\n\nFor more information about how to troubleshoot unhealthy " \
                      "targets, please refer to the following links:" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-unhealthy-checks-ecs/" \
                      "\nhttps://aws.amazon.com/premiumsupport/knowledge-center/troubleshoot-classic-health-checks/ \n\n\n" \
                .format(accountid, timestamp, region, elb_name, tg_arn, "\n".join(str(x) for x in unhealthy_list))
    try:
        sns_client.publish(
            TopicArn=sns_arn,
            Message=message,
            Subject=region.upper() + ' Alarm: unhealthy targets of ELB -- ' + elb_name,
            MessageStructure='string'
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])


def describe_instance_health(elb_name):
    """
	Describe targets health of ClassicLoadBalancer
	"""
    unhealthy_list = []
    unhealthy_instances_id_list = []
    try:
        health_response = elb_client.describe_instance_health(LoadBalancerName=elb_name)
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    for instance in health_response["InstanceStates"]:
        if instance["State"] == "OutOfService":
            unhealthy_list.append(instance)
            unhealthy_instances_id_list.append(instance['InstanceId'])
    put_metric_data(unhealthy_instances_id_list, elb_name)
    logger.info("elb - Unhealthy instances: {}".format(unhealthy_list))
    return unhealthy_list, unhealthy_instances_id_list


def describe_target_health(targetgroup_arn, elb_name, tg_type):
    """
	Describe targets health of Application/NetworkLoadBalancer
	"""
    unhealthy_list = []
    unhealthy_targets_id_port_list = []
    unhealthy_targets_ip_port_list = []
    try:
        response = elbv2_client.describe_target_health(TargetGroupArn=targetgroup_arn)
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    for target in response['TargetHealthDescriptions']:
        if target['TargetHealth']['State'] == 'unhealthy':
            unhealthy_list.append(target)
            unhealthy_targets_id_port_list.append(target['Target']['Id'] + ":" + str(target['Target']['Port']))
    if tg_type == 'ip':
        unhealthy_targets_ip_port_list = unhealthy_targets_id_port_list
    if tg_type == 'instance':
        unhealthy_targets_ip_port_list = get_ondemand_target_port(unhealthy_targets_id_port_list)
    put_metric_data(unhealthy_targets_id_port_list, elb_name)
    logger.info("elbv2 - Unhealthy targets: {}".format(unhealthy_list))
    logger.info("elbv2 - unhealthy_targets_ip_port_list: {}".format(unhealthy_targets_ip_port_list))
    return unhealthy_list, unhealthy_targets_ip_port_list


def get_ondemand_target_port(unhealthy_instances_dimension_list):
    target_id_list = []
    target_port_list = []
    targets_ip_port_list = []
    for target in unhealthy_instances_dimension_list:
        target_id = target.split(':')[0]
        target_port = target.split(':')[1]
        target_id_list.append(target_id)
        target_port_list.append(target_port)
    target_ip_list = get_instance_private_ip(target_id_list)
    for ip, port in zip(target_ip_list, target_port_list):
        targets_ip_port_list.append("{}:{}".format(ip, port))
    return targets_ip_port_list


def put_metric_data(unhealthy_targets, elb_name):
    """
	Put metric to CloudWatch
	"""
    logger.info("\n==Put CloudWatch Metric==\n")
    try:
        cw_client = boto3.client('cloudwatch')
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    for unhealthy_target in unhealthy_targets:
        try:
            cw_client.put_metric_data(
                Namespace='ELB/IdentifyUnhealthyTarget',
                MetricData=[
                    {
                        'MetricName': 'Unhealthy Targets of ' + str(elb_name),
                        'Dimensions': [
                            {
                                'Name': 'TargetId',
                                'Value': unhealthy_target
                            },
                        ],
                        'Value': 1,
                        'Unit': 'Count'
                    },
                ]
            )
        except ClientError as e:
            logger.error(e.response['Error']['Message'])


def describe_targetgroup_ondemand_healthcheck(targetgroup_arn):
    healthcheck_config = {}
    try:
        response = elbv2_client.describe_target_groups(TargetGroupArns=[targetgroup_arn])
    except ClientError as e:
        logger.error(e)
        logger.error("Cannot describe ondemand health check configuration")
    healthcheck_config = response['TargetGroups'][0]
    logger.info("elbv2 - ondemand_healthcheck:", healthcheck_config)
    return healthcheck_config


def describe_elb_ondemand_healthcheck(elb_name):
    try:
        response = elb_client.describe_load_balancers(LoadBalancerNames=[elb_name])
    except ClientError as e:
        logger.error(e)
        logger.error("Cannot describe ondemand health check configuration")
    healthcheck_config = response['LoadBalancerDescriptions'][0]['HealthCheck']
    healthcheck_config['HealthCheckProtocol'] = healthcheck_config['Target'].split(':')[0]
    logger.info("elb - ondemand_healthcheck:", healthcheck_config)
    return healthcheck_config


def get_instance_private_ip(unhealthy_instance_id_list):
    unhealthy_instance_ip_list = []
    response = ec2_client.describe_instances(InstanceIds=unhealthy_instance_id_list)

    for group in response['Reservations']:
        for instance in group['Instances']:
            for eni in instance['NetworkInterfaces']:
                if eni['Attachment']['DeviceIndex'] == 0:
                    for private_ip in eni['PrivateIpAddresses']:
                        if private_ip['Primary'] == True:
                            unhealthy_instance_ip_list.append(private_ip['PrivateIpAddress'])
    return unhealthy_instance_ip_list


def ondemand_tcp_healthcheck(unhealthy_backend_list, healthcheck_config, lbtype):
    '''
	Ondemand TCP health check
	:param unhealthy_backend_list:
	:param healthcheck_config:
	:param lbtype:
	:return: list of TCP health check result of each unhealthy backend
	'''
    ondemand_healthcheck_result_list = []
    if lbtype == 'elb':
        hc_port = int(healthcheck_config['Target'].split(':')[1])
        hc_timeout = int(healthcheck_config['Timeout'])
        logger.info("elb - OnDemand Health Check Timeout: {}".format(str(hc_timeout)))
        for hc_ip in unhealthy_backend_list:
            logger.info("elb - OnDemand Health Check IP: {}".format(hc_ip))
            logger.info("elb - OnDemand Health Check Port: {}".format(hc_port))
            ondemand_healthcheck_result = tcp_health_check(hc_ip, hc_port, hc_timeout)
            ondemand_healthcheck_result_list.append(ondemand_healthcheck_result)

    if lbtype == 'elbv2/nlb':
        hc_timeout = int(healthcheck_config['HealthCheckTimeoutSeconds'])
        logger.info("elbv2 - OnDemand Health Check Timeout: {}".format(str(hc_timeout)))
        for hc_ip_port in unhealthy_backend_list:
            hc_port = int(hc_ip_port.split(':')[1])
            hc_ip = str(hc_ip_port.split(':')[0])
            logger.info("elbv2 - OnDemand Health Check Port: {}".format(hc_port))
            ondemand_healthcheck_result = tcp_health_check(hc_ip, hc_port, hc_timeout)
            ondemand_healthcheck_result_list.append(ondemand_healthcheck_result)
    logger.info("OnDemand TCP Health Check Result:{}".format(str(ondemand_healthcheck_result_list)))
    return ondemand_healthcheck_result_list


def tcp_health_check(ip, port, timeout):
    '''
	TCP health check
	:param ip:
	:param port:
	:param timeout:
	:return: dict of TCP health check result
	'''
    ondemand_healthcheck_result = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect((ip, port))
        logger.error("OnDemand TCP Health Check passed! Backend:{}".format(ip))
        ondemand_healthcheck_result['ip'] = ip
        ondemand_healthcheck_result['check_result'] = "OnDemand TCP Health Check passed! Backend:{}".format(ip)
        s.close()
    except Exception as e:
        logger.info("OnDemand TCP Health Check failed! Backend:{}. Error:{}".format(ip, str(e)))
        logger.error(e)
        ondemand_healthcheck_result['ip'] = ip
        ondemand_healthcheck_result['check_result'] = "OnDemand TCP Health Check failed! Backend:{}. Error:{}".format(
            ip, str(e))
        s.close()
    return ondemand_healthcheck_result


def ondemand_ssl_healthcheck(unhealthy_backend_list, healthcheck_config, lbtype):
    '''
	:param unhealthy_backend_list:
	:param healthcheck_config:
	:param lbtype:
	:return: list of SSL health check result of each unhealthy backend
	'''
    ondemand_healthcheck_result_list = []
    if lbtype == 'elb':
        hc_timeout = int(healthcheck_config['Timeout'])
        hc_timeout = int(healthcheck_config['Timeout'])
        hc_port = int(healthcheck_config['Target'].split(':')[1])
        logger.info("elb - OnDemand Health Check Timeout: {}".format(str(hc_timeout)))
        for hc_ip in unhealthy_backend_list:
            logger.info("elb - OnDemand Health Check IP: {}".format(hc_ip))
            logger.info("elb - OnDemand Health Check Port: {}".format(hc_port))
            ondemand_healthcheck_result = ssl_health_check(hc_ip, hc_port, hc_timeout)
            ondemand_healthcheck_result_list.append(ondemand_healthcheck_result)

    logger.info("OnDemand SSL Health Check Result:{}".format(str(ondemand_healthcheck_result_list)))
    return ondemand_healthcheck_result_list


def ssl_health_check(ip, port, timeout):
    '''
	:param ip:
	:param port:
	:param timeout:
	:return: dict of SSL health check result
	'''
    ondemand_healthcheck_result = {}
    sock = socket.socket(socket.AF_INET)
    context = ssl.create_default_context()
    ssl_socket = context.wrap_socket(sock, server_hostname=ip, do_handshake_on_connect=True)
    ssl_socket.settimeout(timeout)
    try:
        ssl_socket.connect((ip, port))
        logger.info("OnDemand SSL Health Check passed! Backend:{}".format(ip))
        ondemand_healthcheck_result['ip'] = ip
        ondemand_healthcheck_result['check_result'] = "OnDemand SSL Health Check passed! Backend:{}".format(ip)
    except Exception as e:
        logger.error(str(e))
        logger.error("OnDemand SSL Health Check failed! Backend:{}. Error:{}".format(ip, str(e)))
        ondemand_healthcheck_result['ip'] = ip
        ondemand_healthcheck_result['check_result'] = "OnDemand SSL Health Check failed! Backend:{}. Error:{}".format(
            ip, str(e))
    return ondemand_healthcheck_result


def ondemand_http_https_healthcheck(unhealthy_backend_list, healthcheck_config, lbtype):
    '''
	:param unhealthy_backend_list:
	:param healthcheck_config:
	:param lbtype:
	:return: list of HTTP or HTTPs health check result of each unhealthy backend
	'''
    ondemand_healthcheck_result_list = []
    if lbtype == 'elb':
        hc_matcher = 200
        hc_port_and_path = healthcheck_config['Target'].split(':')[1]
        hc_port = int(hc_port_and_path.split('/')[0])
        hc_path = hc_port_and_path.split('/')[1:]
        hc_type = healthcheck_config['HealthCheckProtocol']
        hc_timeout = int(healthcheck_config['Timeout'])
        logger.info("OnDemand Health Check Type: {}".format(hc_type))
        logger.info("OnDemand Health Check Port: {}".format(hc_port))
        logger.info("OnDemand Health Check Path: {}".format(hc_path))
        logger.info("OnDemand Health Check Timeout: {}".format(str(hc_timeout)))
        for hc_ip in unhealthy_backend_list:
            ondemand_healthcheck_result = http_https_health_check(hc_ip, hc_port_and_path, hc_timeout, hc_type)
            ondemand_healthcheck_result_list.append(ondemand_healthcheck_result)

    if lbtype == 'elbv2/alb' or lbtype == 'elbv2/nlb':
        hc_port = healthcheck_config['HealthCheckPort']
        hc_path = healthcheck_config['HealthCheckPath']
        hc_type = healthcheck_config['HealthCheckProtocol']
        hc_timeout = int(healthcheck_config['HealthCheckTimeoutSeconds'])
        hc_matcher = healthcheck_config['Matcher']['HttpCode']
        logger.info("OnDemand Health Check Type: {}".format(hc_type))
        logger.info("OnDemand Health Check Port: {}".format(hc_port))
        logger.info("OnDemand Health Check Path: {}".format(hc_path))
        logger.info("OnDemand Health Check Timeout: {}".format(str(hc_timeout)))

        for hc_ip_port in unhealthy_backend_list:
            if hc_port == 'traffic-port':
                hc_port = int(hc_ip_port.split(':')[1])
                hc_ip = str(hc_ip_port.split(':')[0])
                hc_port_and_path = "{}{}".format(hc_port, hc_path)
                ondemand_healthcheck_result = http_https_health_check(hc_ip, hc_port_and_path, hc_timeout, hc_type,
                                                                      hc_matcher)
                ondemand_healthcheck_result_list.append(ondemand_healthcheck_result)
            else:
                hc_ip = str(hc_ip_port.split(':')[0])
                hc_port_and_path = "{}{}".format(hc_port, hc_path)
                ondemand_healthcheck_result = http_https_health_check(hc_ip, hc_port_and_path, hc_timeout, hc_type,
                                                                      hc_matcher)
                ondemand_healthcheck_result_list.append(ondemand_healthcheck_result)

    logger.info("OnDemand {} Health Check Result:{}".format(hc_type, str(ondemand_healthcheck_result_list)))
    return ondemand_healthcheck_result_list


def http_https_health_check(ip, hc_port_and_path, timeout, hc_type, hc_matcher='200'):
    '''
	:param ip:
	:param hc_port_and_path:
	:param timeout:
	:param hc_type:
	:param hc_matcher:
	:return: dict of HTTP or HTTPs health check result
	'''
    ondemand_healthcheck_result = {}
    hc_url = '{}://{}:{}'.format(hc_type.lower(), ip, hc_port_and_path)
    logger.info("OnDemand HTTP/HTTPS Health Check URL:{}".format(hc_url))
    try:
        r = requests.get(hc_url, verify=False, timeout=timeout)
        if r.status_code == hc_matcher:
            logger.info(
                '{} OnDemand Health Check passed! Backend:{}. OnDemand Health Check Response: HTTP/{}. Expected Health Check Response: {}'.format(
                    hc_type, ip, r.status_code, hc_matcher))
            ondemand_healthcheck_result['ip'] = ip
            ondemand_healthcheck_result[
                'check_result'] = '{} OnDemand Health Check passed! Backend:{}. OnDemand Health Check Response: HTTP/{}. Expected Health Check Response: {}'.format(
                hc_type, ip, r.status_code, hc_matcher)

        else:
            logger.error(
                '{} OnDemand Health Check failed! Backend:{}. OnDemand Health Check Response: HTTP/{}. Expected Health Check Response: {}'.format(
                    hc_type, ip, r.status_code, hc_matcher))
            ondemand_healthcheck_result['ip'] = ip
            ondemand_healthcheck_result[
                'check_result'] = '{} OnDemand Health Check failed! Backend:{}. OnDemand Health Check Response: HTTP/{}. Expected Health Check Response: {}'.format(
                hc_type, ip, r.status_code, hc_matcher)
    except Exception as e:
        logger.error('{} OnDemand Health Check failed! Backend:{}. Error:{}'.format(hc_type, ip, str(e)))
        logger.error(str(e))
        ondemand_healthcheck_result['ip'] = ip
        ondemand_healthcheck_result['check_result'] = '{} OnDemand Health Check failed! Backend:{}. Error:{}'.format(
            hc_type, ip, str(e))
    return ondemand_healthcheck_result
