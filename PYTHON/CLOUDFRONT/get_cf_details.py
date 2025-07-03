import boto3
import json


def get_cloudfront_distribution_config(distribution_id):
    # Create a CloudFront client
    client = boto3.client('cloudfront')

    # Get the distribution configuration
    response = client.get_distribution_config(Id=distribution_id)

    # Extract the configuration part from the response
    config_details = response['DistributionConfig']

    # Convert the configuration details to JSON format
    config_json = json.dumps(config_details, indent=4)

    return config_json


# Example usage
distribution_id = 'E118DNB2L1PTI2'
config_json = get_cloudfront_distribution_config(distribution_id)
print(config_json)
