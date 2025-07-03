import boto3
import json


def get_specific_rds_instance_price(instance_type):
    session = boto3.Session(profile_name="lazypay-prod-role")
    client = session.client('pricing', region_name='us-east-1')

    response = client.get_products(
        ServiceCode='AmazonRDS',
        Filters=[
            {
                'Type': 'TERM_MATCH',
                'Field': 'location',
                'Value': 'Asia Pacific (Mumbai)',
            },
            {
                'Type': 'TERM_MATCH',
                'Field': 'productFamily',
                'Value': 'Database Instance',
            },
            {
                'Type': 'TERM_MATCH',
                'Field': 'instanceType',
                'Value': instance_type,
            },
        ],
        MaxResults=100
    )

    for price_item in response['PriceList']:
        price_item_json = json.loads(price_item)
        instance_type = price_item_json['product']['attributes']['instanceType']

        # Check for On-Demand pricing
        if 'OnDemand' in price_item_json['terms']:
            on_demand_terms = price_item_json['terms']['OnDemand']
            for term in on_demand_terms.values():
                price_dimensions = term['priceDimensions']
                for price_dimension in price_dimensions.values():
                    price_per_unit = price_dimension['pricePerUnit']['USD']
                    description = price_dimension['description']
                    print(
                        f"RDS Instance Type: {instance_type}, On-Demand Price per Hour: ${price_per_unit}, Description: {description}")

get_specific_rds_instance_price("db.t4g.medium")
