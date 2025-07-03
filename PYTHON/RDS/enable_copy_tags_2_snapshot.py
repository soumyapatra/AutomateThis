import boto3


def enable_copy_tags_to_snapshots(db_instance_identifier):
    session = boto3.Session(profile_name="xxxxxxxxfin-sbox-role")
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


if __name__ == "__main__":
    db_instance_identifier = 'mu-pf-rds-qa-common-rw'
    enable_copy_tags_to_snapshots(db_instance_identifier)
