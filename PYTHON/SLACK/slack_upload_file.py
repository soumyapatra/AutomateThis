from slack import *
import sys
import re
from slack.errors import SlackApiError
import os

client = WebClient(token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
alert_slack_channel = "slack_integration_testing"


def postmsg(channel_name, msg):
    channel_id = get_channel_id(channel_name)
    response = client.chat_postMessage(channel=channel_id, text=msg)
    return response


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


def file_upload(channel, file_name):
    try:
        channel_id = get_channel_id(channel)
        # Call the files.upload method using the built-in WebClient
        # Uploading files requires the `files:write` scope
        result = client.files_upload(
            channels=channel_id,
            initial_comment="Here's my file :smile:",
            # The name of the file you're going to upload
            file=file_name,
        )
        return result
    except SlackApiError as e:
        print("Error uploading file: {}".format(e))
        postmsg(alert_slack_channel, "Error uploading file: {}".format(e))


file_upload(alert_slack_channel, "requirement.txt")
