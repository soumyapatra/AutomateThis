from slack import *
import sys
import re
from slack.errors import SlackApiError
import os

# token = os.environ["API_KEY"]
client = WebClient(token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
# client = WebClient(token=token)
USER_GROUP = "pt_stack_alert_group"
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

# private channel for alerting
alert_slack_channel = "slack_integration_testing"


def get_channel_id(channel_name):
    response = client.conversations_list(limit=100, types="private_channel")
    channel_list = []
    if response["ok"]:
        channel_list.extend(response["channels"])
        while response["response_metadata"]["next_cursor"] != "":
            channel_list.append(response["channels"])
    for item in channel_list:
        if item["name"] == channel_name:
            return item["id"]


# postMsg to private channel
def postmsg(channel_name, msg):
    channel_id = get_channel_id(channel_name)
    response = client.chat_postMessage(channel=channel_id, text=msg)
    return response


def get_users_from_grp(grpname):
    response = client.usergroups_list()
    for group in response['usergroups']:
        if group["name"] == grpname:
            members_list = client.usergroups_users_list(usergroup=group["id"])['users']
            return members_list
    return False


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


def create_channel(stack_id, users, owner_name):
    name = f'pt_stack_alert_{stack_id}'
    response = client.conversations_create(name=name.lower(), is_private="true")
    id = get_channel_dict_id(name)
    if response['ok']:
        channel_id = response['channel']['id']
        client.conversations_setTopic(channel=id, topic=f'PT Stack- {stack_id.upper()} Alerts')
        client.conversations_setPurpose(channel=id,
                                        purpose=f'AlertManager/Prometheus Alerts for PT stack\nStack ID: {stack_id}\nStack Owner: {owner_name}')
        client.conversations_invite(channel=channel_id, users=users)
        return f"Channel Created {name}"
    else:
        return False


def valid_email(email_id):
    if re.search(regex, email_id):
        return True
    else:
        return


def get_id_4rm_email(email_id):
    try:
        response = client.users_lookupByEmail(email=email_id)
        if response["ok"]:
            id = response["user"]["id"]
            name = response["user"]["real_name"]
            return {"id": id, "name": name}
        else:
            return False
    except SlackApiError as e:
        print("Failed due to: ", e)
        return False


try:
    if len(sys.argv) != 3:
        print("missing arguments\nUse script as follows: script.py <stack_id> <owner_email_id>")
        postmsg(alert_slack_channel, f'missing args. Got {sys.argv}')
        exit()
    else:
        stack_id = sys.argv[1]
        emailid = sys.argv[2]
        if valid_email(emailid):
            user_list = get_users_from_grp(USER_GROUP)
            if get_id_4rm_email(emailid):
                owner_detail = get_id_4rm_email(emailid)
                owner_id = owner_detail.get("id")
                owner_name = owner_detail.get("name")
                print(f'Got Stack id: {stack_id}\nOwner ID: {owner_id}\nOwner Name: {owner_name}')
                users_list = get_users_from_grp(USER_GROUP)
                user_list.append(owner_id)
                members = ",".join(user_list)
                print(members)
                print(create_channel(stack_id, members, owner_name))
            else:
                print("Email-Id not present in Slack")
                postmsg(alert_slack_channel, f'Email-Id not present in Slack:  {emailid}')
                exit()
        else:
            print("Invalid Email-Id")
            postmsg(alert_slack_channel, f'Invalid Email:  {sys.argv[2]}')
            exit()
except Exception as e:
    print("Failed due to following issues:", e)
    postmsg(alert_slack_channel, f'Slack channel creation for PT stack failed: {e}')
