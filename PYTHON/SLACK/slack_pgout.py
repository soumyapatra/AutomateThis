import os
from slack import WebClient
from slack.errors import SlackApiError
import json

client = WebClient(token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
blocks = """[
            {
                "type": "section",
                "block_id": "no:ih:76107::b5930640b14611ea8d0e89ae1fa31143",
                "text": {
                    "type": "mrkdwn",
                    "text": "*User created a Task*\n*<https://rummycircle.atlassian.net/browse/PGOPS-204?atlOrigin=eyJpIjoiNTVjNzM3N2M2ZTBjNGY2MWJjMWI2NTQ3NGU3ZDkyYjgiLCJwIjoiamlyYS1zbGFjay1pbnQifQ|PGOPS-204 outage test>*",
                    "verbatim": false
                },
                "accessory": {
                    "type": "overflow",
                    "action_id": "{\"issueId\":\"76107\",\"instanceId\":\"jira:07c95331-d630-4966-93db-12238d077366\",\"projectId\":\"12201\"}",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Watch",
                                "emoji": true
                            },
                            "value": "watch"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Assign",
                                "emoji": true
                            },
                            "value": "assign"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Transition",
                                "emoji": true
                            },
                            "value": "transition"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Comment",
                                "emoji": true
                            },
                            "value": "comment"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Why am I seeing this?",
                                "emoji": true
                            },
                            "value": "why"
                        }
                    ]
                }
            },
            {
                "type": "context",
                "block_id": "no:cx:76107::b5bc8740b14611ea8d0e89ae1fa31143",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Status: *Open*",
                        "verbatim": false
                    },
                    {
                        "fallback": "64x64px image",
                        "image_url": "https://rummycircle.atlassian.net/secure/viewavatar?size=xlarge&avatarId=10318&avatarType=issuetype&format=png",
                        "image_width": 64,
                        "image_height": 64,
                        "image_bytes": 770,
                        "type": "image",
                        "alt_text": "Task"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Type: *Task*",
                        "verbatim": false
                    },
                    {
                        "fallback": "65x65px image",
                        "image_url": "https://product-integrations-cdn.atl-paas.net/icons/unknown-user.png",
                        "image_width": 65,
                        "image_height": 65,
                        "image_bytes": 2589,
                        "type": "image",
                        "alt_text": "Unassigned"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Assignee: *Unassigned*",
                        "verbatim": false
                    },
                    {
                        "fallback": "48x48px image",
                        "image_url": "https://product-integrations-cdn.atl-paas.net/jira-priority/medium.png",
                        "image_width": 48,
                        "image_height": 48,
                        "image_bytes": 1196,
                        "type": "image",
                        "alt_text": "Medium"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Priority: *Medium*",
                        "verbatim": false
                    }
                ]
            }
        ]"""

try:
    response = client.chat_postMessage(
        channel='#pgops-204',
        text="User created a Task PGOPS-204 outage test", blocks= [
            {
                "type": "section",
                "block_id": "no:ih:76107::b5930640b14611ea8d0e89ae1fa31143",
                "text": {
                    "type": "mrkdwn",
                    "text": "*User created a Task*\n*<https://rummycircle.atlassian.net/browse/PGOPS-204?atlOrigin=eyJpIjoiNTVjNzM3N2M2ZTBjNGY2MWJjMWI2NTQ3NGU3ZDkyYjgiLCJwIjoiamlyYS1zbGFjay1pbnQifQ|PGOPS-204 outage test>*",
                    "verbatim": False
                },
                "accessory": {
                    "type": "overflow",
                    "action_id": "{\"issueId\":\"76107\",\"instanceId\":\"jira:07c95331-d630-4966-93db-12238d077366\",\"projectId\":\"12201\"}",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Watch",
                                "emoji": True
                            },
                            "value": "watch"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Assign",
                                "emoji": True
                            },
                            "value": "assign"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Transition",
                                "emoji": True
                            },
                            "value": "transition"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Comment",
                                "emoji": True
                            },
                            "value": "comment"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Why am I seeing this?",
                                "emoji": True
                            },
                            "value": "why"
                        }
                    ]
                }
            },
            {
                "type": "context",
                "block_id": "no:cx:76107::b5bc8740b14611ea8d0e89ae1fa31143",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Status: *Open*",
                        "verbatim": False
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Type: *Task*",
                        "verbatim": False
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Assignee: *Unassigned*",
                        "verbatim": False
                    },
                    {
                        "type": "mrkdwn",
                        "text": "Priority: *Medium*",
                        "verbatim": False
                    }
                ]
            }
        ])
    #assert response["message"]["text"] == "Hello world!"

    #response_create_channel = client.conversations_create(name="pgout-123", user_id="U0153R65Y79", is_private="true")
    #print(response_create_channel)
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
