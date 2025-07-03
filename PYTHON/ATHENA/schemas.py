import boto3

glu=boto3.client('glue')
resp = glu.get_databases()


dbs=[]
for db in resp['DatabaseList']:
    dbs.append(db['Name'])

print(dbs)
