from slack import *

client = WebClient(token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


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


def get_users_from_grp(grpname):
    response = client.usergroups_list()
    user_list = []
    for group in response['usergroups']:
        if group["name"] == grpname:
            members_list = client.usergroups_users_list(usergroup=group["id"])['users']
            members = ",".join(members_list)
            return members
    return False


print(get_users_from_grp("outage-group"))
