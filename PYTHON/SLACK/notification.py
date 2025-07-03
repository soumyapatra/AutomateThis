import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


ENCRYPTED_HOOK_URL = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

SLACK_CHANNEL = "#cwalarm_notification"
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler():


    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': "HI"
    }


    req = Request(ENCRYPTED_HOOK_URL, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

lambda_handler()
