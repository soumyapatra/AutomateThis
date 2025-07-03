import boto3
import json

ROLE = "xxxxxxxx-prod-role"
REGION = "ap-south-1"


def get_s3_bucket_configuration(bucket_name, role_name):
    # Create a session using your credentials
    session = boto3.Session(profile_name=role_name)
    # Create an S3 client
    s3_client = session.client('s3')

    # Get the bucket policy
    bucket_policy = s3_client.get_bucket_policy(Bucket=bucket_name)
    bucket_policy_json = json.loads(bucket_policy['Policy'])

    # Get bucket CORS configuration
    cors_response = s3_client.get_bucket_cors(Bucket=bucket_name)
    cors_configuration = cors_response['CORSRules']

    # Get bucket ACL
    acl_response = s3_client.get_bucket_acl(Bucket=bucket_name)
    bucket_acl = acl_response['Grants']

    # Compile all configurations into a single dictionary
    bucket_configurations = {
        'BucketPolicy': bucket_policy_json,
        'CORSConfiguration': cors_configuration,
        'ACL': bucket_acl
    }

    # Print the output in JSON format
    print(json.dumps(bucket_configurations, indent=4))


# Replace with your bucket name
bucket_name = 'your-bucket-name'
get_s3_bucket_configuration(bucket_name, ROLE)
