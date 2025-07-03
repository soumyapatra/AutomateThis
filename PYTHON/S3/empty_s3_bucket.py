import argparse

import boto3

parser = argparse.ArgumentParser(description="")
parser.add_argument("-r", "--role-name", type=str, help="AWS Role", required=True)
parser.add_argument("-b", "--bucket-name", type=str, help="S3 Bucket Name", required=True)
parser.add_argument("-a", "--region", type=str, help="AWS region", required=False, default="ap-south-1")
args = parser.parse_args()
#
session = boto3.Session(profile_name=args.role_name, region_name=args.region)
#s3 = session.resource('s3')
#bucket = s3.Bucket(args.bucket_name)
#
#bucket.objects.all().delete()

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time

# Configure logging
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    filename=f'/tmp/{args.bucket_name}_s3_deletion.log',
    filemode='a',  # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()

s3 = session.client('s3')
bucket_name = args.bucket_name


def delete_object_version(key, version_id):
    try:
        s3.delete_object(Bucket=bucket_name, Key=key, VersionId=version_id)
        logger.info(f"Deleted: {key} (VersionId: {version_id})")
    except Exception as e:
        logger.error(f"Error deleting {key} (VersionId: {version_id}): {e}")
        return key, version_id  # Return the key and version_id if deletion failed


def delete_objects(keys_versions):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_key_version = {executor.submit(delete_object_version, key, version_id): (key, version_id) for
                                 key, version_id in keys_versions}
        for future in as_completed(future_to_key_version):
            key, version_id = future_to_key_version[future]
            if future.exception() is not None:
                logger.error(f"Exception for {key} (VersionId: {version_id}): {future.exception()}")
                # Retry failed deletions
                delete_object_version(key, version_id)


def paginate_and_delete():
    paginator = s3.get_paginator('list_object_versions')
    page_iterator = paginator.paginate(Bucket=bucket_name)

    for page in page_iterator:
        keys_versions = [(obj['Key'], obj['VersionId']) for obj in page.get('Versions', [])]
        keys_versions += [(marker['Key'], marker['VersionId']) for marker in page.get('DeleteMarkers', [])]
        if keys_versions:
            delete_objects(keys_versions)
        else:
            logger.info("No more keys or delete markers to delete.")


if __name__ == "__main__":
    start_time = time.time()
    paginate_and_delete()
    end_time = time.time()
    logger.info(f"Completed in {end_time - start_time} seconds")
