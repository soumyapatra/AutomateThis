import boto3

glu=boto3.client('glue')
resp = glu.get_databases()

print(resp['DatabaseList'])

dbs=[]
for db in resp['DatabaseList']:
    dbs.append(db['Name'])

print(dbs)

for db in dbs:
    tables=[]
    response = glu.get_tables(DatabaseName=db)
    for table in response['TableList']:
        table_name = table['Name']
        for columns in table['StorageDescriptor']['Columns']:
            column_name = columns['Name']
            type = columns['Type']
            #print('Column_name', columns['Name'], 'type', columns['Type'])
            print(f'DB:{db}\n---------------\n{table_name}\n{column_name} {type}\n\n\n')
