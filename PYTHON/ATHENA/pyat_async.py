from pyathena import connect
from pyathena.pandas_cursor import PandasCursor


query = """SELECT * FROM "stage_alb_log"."alb_fp_priv_ext2_stage_pt_alb" limit 10"""
cursor = connect(s3_staging_dir='s3://xxxxxxxxxxxxxxxxxxxxxx/athena_outputs/',region_name='ap-southeast-1',cursor_class=PandasCursor).cursor()
df = cursor.execute(query).as_pandas()
print(cursor.state)
print(cursor.state_change_reason)
print(cursor.completion_date_time)
print(cursor.submission_date_time)
print(cursor.data_scanned_in_bytes)
print(cursor.execution_time_in_millis)
print(cursor.output_location)
print(df.describe())
