import boto3

glu=boto3.client('glue')
resp = glu.get_databases()


dbs=[]
for db in resp['DatabaseList']:
    dbs.append(db['Name'])

#print(dbs)

ret=[]
for db in dbs:
    tables=[]
    response = glu.get_tables(DatabaseName=db)
    for table in response['TableList']:
        td = []
        table_name = table['Name']
        for columns in table['StorageDescriptor']['Columns']:
            column_name = columns['Name']
            type = columns['Type']
            #print('Column_name', columns['Name'], 'type', columns['Type'])
            #print(column_name,type)
            td.append((column_name,type))
        ret.append((table_name,td))
print(ret)
