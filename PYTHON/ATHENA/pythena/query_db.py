import boto3
import pythena

aws_region = 'ap-southeast-1'


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


def get_cf_dict(region):
    db_list = get_db(region)
    cf_partition = [{'Name': 'year', 'Type': 'string'}, {'Name': 'month', 'Type': 'string'},
                    {'Name': 'day', 'Type': 'string'}, {'Name': 'hour', 'Type': 'string'}]
    glue = boto3.client('glue')
    cf_dict = []
    for db in db_list:
        athena_client = pythena.Athena(database=db, region=region)
        table_list = get_table(db, region)
        for table in table_list:
            response = glue.get_table(DatabaseName=db, Name=table)
            if 'PartitionKeys' in response['Table']:
                partitions = response['Table']['PartitionKeys']
                if len(partitions) == 4:
                    if partitions == cf_partition:
                        location = response['Table']['StorageDescriptor']['Location']
                        id = location.split('/')[-1]
                        cf_dict.append({'id': id, 'table': table, 'db': db, 's3_log': location})
            else:
                continue
    return cf_dict


print(get_cf_dict(aws_region))
