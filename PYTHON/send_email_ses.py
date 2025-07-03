import boto3
from botocore.exceptions import ClientError


def send_email(sender, recipient, aws_region, subject, body_text, body_html):
    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=aws_region)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=sender,
        )

    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


# Input details
sender = "noreply@xxx.io"  # Must be verified in SES
recipient = "soumyaranjan.patra@xxxx.io"
aws_region = "ap-south-1"  # Replace with your region
subject = "Test Email from AWS SES"
body_text = "Hello,\r\nThis is a test email sent via AWS SES."
body_html = """<html>
<head></head>
<body>
  <h1>Hello!</h1>
  <p>This is a test email sent via <a href='https://aws.amazon.com/ses/'>AWS SES</a>.</p>
</body>
</html>
"""

send_email(sender, recipient, aws_region, subject, body_text, body_html)
