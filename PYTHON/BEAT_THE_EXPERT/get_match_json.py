import requests
import os
import json
import boto3

REGION = ""
match_id = 12660
file_name = f'./{match_id}_details.json'
s3_bucket = ""
SNS_ARN = ""


def upload_to_s3(filename, bucket_name, key, region):
    s3 = boto3.client('s3', region_name=region)
    s3.upload_file(filename, bucket_name, key)
    return


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return response


def lambda_handler(event, context):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Login-Context': '{loginId:loginId,isTest:0,userIP:dummyIP, agentName:null,agentGroup:null, source:TestSource,time:1234566333, sessionId:dummySessionId,state:null,userId:123,channelId:1}',
        }
        url = 'http://10.200.105.229:8080/fantasycoreservice/api/lobby/matches/' + str(match_id) + '/squad'
        response = requests.get(url, headers=headers)

        status_code = response.status_code
        if status_code != 200:
            print("NON 200 status code returned")
            func_name = context.function_name
            pub_sns(SNS_ARN, f"{func_name} Lambda failed: ", f"NON 200 status code returned for URL: {url}")

        x = response.json()

        with open(file_name, 'w') as out:
            json.dump(x, out)
        upload_to_s3(file_name, s3_bucket, "match_details", REGION)

    except Exception as e:
        print("Failed: ", e)
        func_name = context.function_name
        pub_sns(SNS_ARN, f"{func_name} Lambda failed: {e}", "Error in Lambda Execution")
