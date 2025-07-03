import pyathena
import pyathena.connection as connect
query = """SELECT * FROM "stage_alb_log"."alb_fp_priv_ext2_stage_pt_alb" limit 10"""

cursor=connect(s3_staging_dir='xxxxxxxxxxxxxxxxxx/athena_outputs/',
                 region_name='ap-southeast-1').cursor()
cursor.execute(query)
for row in cursor:
    print(row)
