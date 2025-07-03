import configparser
import os

import boto3

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()


def tag_sqs_queues(role_name):
    session = boto3.Session(profile_name=role_name, region_name="ap-south-1")

    sqs = session.client('sqs')

    response = sqs.list_queues()

    if 'QueueUrls' in response:
        for queue_url in response['QueueUrls']:
            queue_name = queue_url.split('/')[-1]

            tags_response = sqs.list_queue_tags(QueueUrl=queue_url)
            tags = tags_response.get('Tags', {})
            #            print(tags)

            if 'Name' not in tags:
#                sqs.tag_queue(
#                    QueueUrl=queue_url,
#                    Tags={
#                        'Name': queue_name
#                    }
#                )
                print(f"Applied 'Name' tag to queue: {queue_url} with value: {queue_name}")
            else:
                print(f"'Name' tag already present for queue: {queue_url}")
    else:
        print("No SQS queues found.")


if __name__ == "__main__":
    for role in roles:
        tag_sqs_queues(role)
