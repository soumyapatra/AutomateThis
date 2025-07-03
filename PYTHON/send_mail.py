import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Initialize a session using AWS credentials
session = boto3.Session(
    aws_access_key_id='XXXXXXXXXXXXXXXXXXXXX',
    aws_secret_access_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    region_name='ap-south-1'
)

# Initialize the SES client
ses = session.client('ses')

try:
    response = ses.send_email(
        Source='xxxxxxxxxxx@xxxxx.xx',
        Destination={
            'ToAddresses': [
                'xxxxxxxxxxxx@xxxxxxxxxx.xx',
            ],
        },
        Message={
            'Subject': {
                'Data': 'Test Email',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': 'This is a test email sent from AWS SES.',
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    print("Email sent successfully!", response)
except NoCredentialsError:
    print("Error: No AWS credentials found.")
except PartialCredentialsError:
    print("Error: Incomplete AWS credentials.")
except Exception as e:
    print("Error:", e)
