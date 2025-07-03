import boto3
from botocore.exceptions import ClientError

role_name = "xxxxxxxxfin-sbox-role"
role_session = boto3.Session(profile_name=role_name)
s3 = role_session.client('s3')

bucket_name = 'omkar-test-112333'
current_version_transition = 180
str_class_list = ["GLACIER", "STANDARD_IA", "ONEZONE_IA", "INTELLIGENT_TIERING", "DEEP_ARCHIVE", "GLACIER_IR"]
str_transition_class = "GLACIER"
str_class_transition_days = 180
class_transition_rule_id = f"move-to-{str_transition_class}-after-{str_class_transition_days}"
common_rule_id = f"Remove"
obj_noncurrent_version_expiry = 30
abort_incomplete_multipart_upload_expiry = 7


def get_bucket_lf_rules(name, session):
    s3_client = session.client("s3")
    try:
        resp = s3_client.get_bucket_lifecycle_configuration(Bucket=name)
        return resp["Rules"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
            return False


def put_bucket_lf_rules(name, session, rules):
    s3_client = session.client("s3")
    resp = s3_client.put_bucket_lifecycle_configuration(Bucket=name, LifecycleConfiguration=rules)
    if resp["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return


if not get_bucket_lf_rules(bucket_name, role_session):
    lc_rule = {'Rules': [
        {
            "Expiration": {
                "ExpiredObjectDeleteMarker": True
            },
            "ID": "remove-delete_markers-incomplete_multipart_upload-non_current_version_obj",
            "Filter": {},
            "Status": "Enabled",
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": obj_noncurrent_version_expiry
            },
            "AbortIncompleteMultipartUpload": {
                "DaysAfterInitiation": abort_incomplete_multipart_upload_expiry
            }
        },
        {
            "ID": class_transition_rule_id,
            "Filter": {},
            "Status": "Enabled",
            "Transitions": [
                {
                    "Days": str_class_transition_days,
                    "StorageClass": str_transition_class
                }
            ]
        }
    ]}
    put_bucket_lf_rules(bucket_name, role_session, lc_rule)
