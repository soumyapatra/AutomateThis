import boto3
import json

role_name = "lazypay-prod-role"


def list_msk_connect_clusters(role_name):
    session = boto3.Session(profile_name=role_name, region_name="ap-south-1")
    client = session.client('kafkaconnect')

    response = client.list_connectors()
    connectors = response.get('connectors', [])

    if not connectors:
        print("No MSK Connect clusters found.")
        return

    for connector in connectors:
        connector_name = connector['connectorName']
        connector_arn = connector['connectorArn']
        print(connector_arn)

        connector_info = client.describe_connector(connectorArn=connector_arn)
        print(json.dumps(connector_info, indent=4, sort_keys=True, default=str))
        for plugin in connector_info["plugins"]:
            print(plugin["customPlugin"]["customPluginArn"])

        print(f"Connector Name: {connector_name}")
        print(f"Connector ARN: {connector_arn}")

        if custom_plugin_arns:
            print("Custom Plugin ARNs:")
            for plugin_arn in custom_plugin_arns:
                print(f"  - {plugin_arn}")
        else:
            print("No custom plugins associated with this connector.")

        print("-" * 40)


if __name__ == "__main__":
    list_msk_connect_clusters(role_name)