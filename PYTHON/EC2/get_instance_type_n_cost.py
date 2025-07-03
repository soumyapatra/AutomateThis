import boto3
import json


def get_running_instances_with_names(region):
    """
    Retrieves all running EC2 instances in a specific region along with their instance types and names.
    """
    ec2_client = boto3.client('ec2', region_name=region)
    response = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            instance_name = ''
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
            instances.append((instance_id, instance_type, instance_name))

    return instances


def get_pricing_instance_type(instance_type, region='ap-south-1'):
    """
    Retrieves the on-demand hourly cost for an EC2 instance type.
    """
    pricing_client = boto3.client('pricing', region_name='us-east-1')  # Pricing API is centralized
    location_map = {
        'ap-south-1': 'Asia Pacific (Mumbai)',
        # Add other location mappings if necessary
    }

    price = None
    try:
        response = pricing_client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location_map[region]},
            ]
        )

        for price_item in response.get('PriceList', []):
            price_info = json.loads(price_item)
            terms = price_info.get('terms', {}).get('OnDemand', {})
            for _, details in terms.items():
                for _, dimension_info in details['priceDimensions'].items():
                    price = dimension_info['pricePerUnit'].get('USD', None)
                    if price:
                        return float(price)
    except Exception as e:
        print(f"Error retrieving price for {instance_type}: {e}")

    return price


def calculate_monthly_cost(hourly_price):
    """
    Calculate the approximate monthly cost based on an hourly rate.
    """
    # Approximate hours in a month
    hours_in_month = 730
    return hourly_price * hours_in_month


def main():
    region = 'ap-south-1'  # Define the AWS region
    instances = get_running_instances_with_names(region)

    for instance_id, instance_type, instance_name in instances:
        hourly_price = get_pricing_instance_type(instance_type, region)
        if hourly_price is not None:
            monthly_price = calculate_monthly_cost(hourly_price)
            print(f"Instance ID: {instance_id}, Name: {instance_name}, Instance Type: {instance_type}, "
                  f"Hourly Price: ${hourly_price:.4f}, Monthly Price: ${monthly_price:.2f}")
        else:
            print(f"Price not found for instance type: {instance_type}")


if __name__ == "__main__":
    main()