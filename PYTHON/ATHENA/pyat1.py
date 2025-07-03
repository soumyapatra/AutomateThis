from pyathena import connect
import pandas as pd
from pyathena.util import as_pandas

query = """SELECT * FROM "stage_alb_log"."alb_fp_priv_ext2_stage_pt_alb" limit 10"""
cursor = connect(s3_staging_dir='s3://xxxxxxxxxxxxxxxx/athena_outputs/',region_name='ap-southeast-1').cursor()
print(cursor.output_location)
