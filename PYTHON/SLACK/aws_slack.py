import requests
import json


def slack_send(slack_channel, message, title, hook_url = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"):
    slack_msg = {
        "username": "ALARM",
        "mrkdwn": 'true',
        'icon_emoji': ':alarm_clock:',
        "channel": slack_channel,
        "attachments": [
            {
                "fallback": "CloudWatch Alarm Creation",
                "author_name": "AWS CloudWatch",
                "color": "#7B68EE",
                "title": title,
                "text": message,
            }
        ]
    }
    try:
        requests.post(hook_url, data=json.dumps(slack_msg))
    except Exception as e:
        print("Failed:", e)
