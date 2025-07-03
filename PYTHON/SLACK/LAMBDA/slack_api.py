import boto3
import json
import re
from slack import *
import traceback
import os

ALERT_SNS_ARN = os.environ['ALERT_SNS_ARN']
JIRA_ISSUE = os.environ['JIRA_ISSUE']
client = WebClient(token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
task_create_pattern = f"created a Task ({JIRA_ISSUE}-[0-9]*)"
issue_comment_pattern = f"commented on ({JIRA_ISSUE}-[0-9]*)"
issue_transition_pattern = f"({JIRA_ISSUE}-[0-9]*)"
USER_GROUP = os.environ['USER_GROUP']
default_members = "U6KEMSP51,UD0F5F1D5"


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return response


def get_channel_dict():
    response = client.conversations_list(types="public_channel,private_channel")
    channel_list = []
    name_list = []
    for item in response:
        for channel in item['channels']:
            channel_list.append(channel)
    for channel in channel_list:
        name_list.append({"id": channel["id"], "name": channel["name"]})
    return name_list


def get_channel_dict_id(name):
    response = client.conversations_list(types="public_channel,private_channel")
    channel_list = []
    name_list = []
    for item in response:
        for channel in item['channels']:
            channel_list.append(channel)
    for channel in channel_list:
        if channel['name'] == name:
            return channel['id']
    return False


def get_channel_names():
    response = client.conversations_list(types="public_channel,private_channel")
    channel_list = []
    name_list = []
    for item in response:
        for channel in item['channels']:
            channel_list.append(channel)
    for channel in channel_list:
        name_list.append(channel["name"])
    return name_list


def get_bot_id(name):
    response = client.users_list()
    for user in response['members']:
        if user['name'] == name:
            id = user['profile']['bot_id']
    return id


def post_msg(channel_id, blocks, text):
    response = client.chat_postMessage(channel=channel_id, blocks=blocks, text=text)
    return response


def create_channel(name, users):
    response = client.conversations_create(name=name.lower(), is_private="true")
    id = get_channel_dict_id(name)
    if response['ok']:
        channel_id = response['channel']['id']
        client.conversations_setTopic(channel=id, topic=f'JIRA ISSUE {name.upper()}')
        client.conversations_setPurpose(channel=id,
                                        purpose=f'Please follow SOP checklist given below: \n  https://rummycircle.atlassian.net/wiki/spaces/DEVOPSSRE/pages/498106433/SOP+Checklist+to+be+followed+in+case+of+Outage+or+Service+impact')
        client.conversations_invite(channel=channel_id, users=users)


def get_users_from_grp(grpname):
    response = client.usergroups_list()
    user_list = []
    for group in response['usergroups']:
        if group["name"] == grpname:
            members_list = client.usergroups_users_list(usergroup=group["id"])['users']
            members = ",".join(members_list)
            return members
    return False


def lambda_handler(event, context):
    try:
        print("EVENT: ", event)
        lamb = boto3.client('lambda')
        print(json.dumps(event))
        if "challenge" in event:
            chlg = event["challenge"]
            return {
                "challenge": chlg
            }

        if "event" in event:
            slack_event = event['event']
            if slack_event['type'] == "message":
                jira_bot_id = get_bot_id("jirabot")
                print(jira_bot_id)
                if "bot_id" in slack_event and slack_event['bot_id'] == jira_bot_id:
                    print("Got JIRA BOT", jira_bot_id)
                    chat_block = slack_event['blocks']
                    channel_names = get_channel_names()
                    if re.search(task_create_pattern, slack_event['text']):
                        print("created issue")
                        issue_no = re.findall(task_create_pattern, slack_event['text'])[0]
                        print(issue_no)
                        issue_no = issue_no.lower()

                        if issue_no not in channel_names:
                            if get_users_from_grp(USER_GROUP):
                                group_users = get_users_from_grp(USER_GROUP)
                                create_channel(issue_no, group_users)
                            else:
                                print("USER GROUP NOT PRESENT IN SLACK. ADDING DEFAULT MEMBERS")
                                create_channel(issue_no, default_members)

                        channel_dict = get_channel_dict()
                        del chat_block[1]
                        del chat_block[0]['accessory']
                        for item in channel_dict:
                            if item['name'] == issue_no:
                                post_msg(item['id'], chat_block, slack_event['text'])
                        return {
                            'statusCode': 200,
                            'body': json.dumps('done')
                        }
                    elif re.search(issue_transition_pattern, slack_event['text']):
                        print("issue updated")
                        issue_no = re.findall(issue_transition_pattern, slack_event['text'])[0]
                        issue_no = issue_no.lower()
                        if issue_no not in channel_names:
                            if get_users_from_grp(USER_GROUP):
                                group_users = get_users_from_grp(USER_GROUP)
                                create_channel(issue_no, group_users)
                            else:
                                print("USER GROUP NOT PRESENT IN SLACK. ADDING DEFAULT MEMBERS")
                                create_channel(issue_no, default_members)
                        for block in chat_block:
                            if block['type'] == "context":
                                element_list = block['elements']
                                del element_list[1]
                                del element_list[2]
                                del element_list[3]
                        if "accessory" in chat_block[0]:
                            del chat_block[0]['accessory']
                        channel_dict = get_channel_dict()
                        for item in channel_dict:
                            if item['name'] == issue_no:
                                post_msg(item['id'], chat_block, slack_event['text'])
                        return {
                            'statusCode': 200,
                            'body': json.dumps('done')
                        }

        return {
            'statusCode': 200,
            'body': json.dumps('done')
        }
    except Exception as e:
        print("Issue occurred:", e)
        traceback.print_exc()
        message = f'Issue in slack api function: {e}'
        pub_sns(ALERT_SNS_ARN, message,
                f'Issue in SLACK API Lambda {context.function_name}\nRequest ID: {context.aws_request_id}')
