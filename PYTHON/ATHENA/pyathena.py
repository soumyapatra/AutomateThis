from pyathena import connect

cursor = connect(s3_staging_dir='s3://xxxxxxxxxxxxxxxxxxxxxxx/athena_outputs/',
                 region_name='ap-southeast-1').cursor()
cursor.execute("show databases")
print(cursor.description)
print(cursor.fetchall())

