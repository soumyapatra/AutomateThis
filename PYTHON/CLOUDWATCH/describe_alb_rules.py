import boto3
import requests
import json
import os

REGION = os.environ["REGION"]
ALB_ARNS = os.environ["ALB_ARNS"]
HOOK_URL = os.environ["HOOK_URL"]
ALERT_CHANNEL = os.environ["ALERT_CHANNEL"]
FAILED_CHANNEL = os.environ["FAILED_CHANNEL"]

client = boto3.client('elbv2', region_name=REGION)


def slack_send(slack_channel, message, sub, title):
    channels = []
    if slack_channel != "":
        channels.append(slack_channel)
    for channel in channels:
        slack_msg = {
            "username": "ALARM",
            "mrkdwn": 'true',
            'icon_emoji': ':robot_face:',
            "channel": channel,
            "attachments": [
                {
                    "fallback": sub,
                    "author_name": "AWS",
                    "color": "#7B68EE",
                    "title": title,
                    "text": message,
                }
            ]
        }
        try:
            requests.post(HOOK_URL, data=json.dumps(slack_msg))
        except Exception as e:
            print("Failed:", e)


def get_listeners(alb_arn):
    response = client.describe_listeners(LoadBalancerArn=alb_arn)
    listener_list = []
    for listener in response["Listeners"]:
        listener_list.append(listener["ListenerArn"])
    return listener_list


def get_listener_rule_count(list_arn):
    response = client.describe_rules(ListenerArn=list_arn)
    rule_count = 0
    for rule in response["Rules"]:
        rule_count += 1
    return rule_count


def lambda_handler(event, context):
    try:
        alb_list = [x.strip() for x in ALB_ARNS.split(",")]

        for alb in alb_list:
            alb_name = alb.split("/")[-2]
            listener_arns = get_listeners(alb)
            for listener in listener_arns:
                if get_listener_rule_count(listener) >= 90:
                    listener_count = get_listener_rule_count(listener)
                    slack_send(ALERT_CHANNEL,
                               f"Please destroy unused stacks.\nALB {alb_name} Listener Rule Limit Reached: {listener_count}",
                               f"Stack Limit Alert", "Stack Limit Alert")
    except Exception as e:
        function_name = context.function_name
        slack_send(FAILED_CHANNEL, f"Issue while running ALB rule limit lambda: {function_name}\nError: {e}", "Lambda Failed Alert", "Lambda Failed Alert")