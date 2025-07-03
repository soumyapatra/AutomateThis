import os
import re

import pandas as pd
import boto3

home_dir = os.path.expanduser('~')
file_path = f'{home_dir}/Tagging.csv'
REGION = "ap-south-1"


def enable_copy_tags_to_snapshots(db_instance_identifier, role_name):
    session = boto3.Session(profile_name=role_name, region_name=REGION)
    rds_client = session.client('rds')

    try:
        response = rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            CopyTagsToSnapshot=True
        )
        print(f"Successfully enabled CopyTagsToSnapshot for DB instance: {db_instance_identifier}")
        print(response)
    except Exception as e:
        print(f"Error enabling CopyTagsToSnapshot for DB instance: {db_instance_identifier}")
        print(e)


def enable_copy_tags_to_snapshot_docdb(cluster_identifier, role_name):
    session = boto3.Session(profile_name=role_name, region_name=REGION)
    client = session.client('docdb')

    try:
        # Modify the cluster to enable copy tags to snapshot
        response = client.modify_db_cluster(
            DBClusterIdentifier=cluster_identifier,
            CopyTagsToSnapshot=True
        )
        print(f"Successfully enabled Copy Tags to Snapshot for cluster: {cluster_identifier}")
        print(response)
    except Exception as e:
        print(f"Error enabling Copy Tags to Snapshot for cluster: {cluster_identifier}")
        print(e)


df = pd.read_csv(file_path, keep_default_na=False)

for index, row in df.iterrows():
    acct_name = row["Account Name"]
    role = f"{acct_name}-role"
    rds_inst_id = row["rds_instance_id"]
    db_engine = row["DB Engine"]
    if db_engine == "docdb":
        enable_copy_tags_to_snapshot_docdb(rds_inst_id, role)
    else:
        enable_copy_tags_to_snapshots(rds_inst_id, role)
