import boto3


def get_table(db, region):
    glue_client = boto3.client('glue', region_name=region)
    table_list = []
    table_json = []
    response = glue_client.get_tables(DatabaseName=db)
    table_json.extend(response['TableList'])
    while 'NextToken' in response:
        response = glue_client.get_tables(DatabaseName=db, NextToken=response['NextToken'])
        table_json.extend(response['TableList'])
    for i in table_json:
        table_list.append(i['Name'])
    return table_list


def get_db(region):
    glue_client = boto3.client('glue', region_name=region)
    db_json = []
    response = glue_client.get_databases()
    db_json.extend(response['DatabaseList'])
    while 'NextToken' in response:
        response = glue_client.get_databases(NextToken=response['NextToken'])
        db_json.extend(response['DatabaseList'])
    db_list = []
    for i in db_json:
        db_list.append(i['Name'])
    return db_list

db_list = get_db('ap-southeast-1')
for db in db_list:
    table_list = get_table(db, region='ap-southeast-1')
    print(f'DB------------------\n{db}\ntables------------------\n{table_list}\n\n')