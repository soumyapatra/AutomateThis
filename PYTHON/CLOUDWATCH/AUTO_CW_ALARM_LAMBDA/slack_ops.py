import os
import requests
import json

HOOK_URL = os.environ['HOOK_URL']


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
