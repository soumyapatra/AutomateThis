import boto3

dynamodb = boto3.resource('dynamodb')

table_name = 'staff'
table_names = [table.name for table in dynamodb.tables.all()]

if table_name in table_names:
    table = dynamodb.Table('staff')

    table.put_item(
        Item={
            'username': 'ruanb',
            'first_name': 'ruan',
            'last_name': 'bekker',
            'age': 30,
            'account_type': 'administrator',
        }
    )

    print(table.item_count)
else:
    table = dynamodb.create_table(
        TableName='staff',
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'last_name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'last_name',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    table.meta.client.get_waiter('table_exists').wait(TableName='staff')
