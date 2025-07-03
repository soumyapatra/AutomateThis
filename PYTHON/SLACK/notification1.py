from __future__ import print_function

import boto3
import json
import logging
import os
import datetime

from dateutil.tz import tzlocal

from urllib.request import Request, urlopen, URLError, HTTPError

HOOK_URL = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

now = datetime.datetime.now(tzlocal()) - datetime.timedelta(hours=8)

fmt1 = now.strftime('%A, %B %d, %Y - %H:%m')
logger.info('fmt1 = %s' % (fmt1))


def lambda_handler():

    slack_message = {
        'channel': "#monitoring",
        'text': "Hello World @ " + fmt1
    }

    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))

    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
        
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
        
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

lambda_handler()
