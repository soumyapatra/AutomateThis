import boto3

# Create an SNS client
sns = boto3.client('sns')

# Publish a simple message to the specified SNS topic
response = sns.publish(
    TopicArn='arn:aws:REDACTED',    
    Message='Hello World!',    
)

# Print out the response
print(response)
