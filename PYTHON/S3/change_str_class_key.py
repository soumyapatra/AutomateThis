import boto3
import sys
import csv

s3 = boto3.client('s3', region_name="ap-south-1")


def change_str_class(bucket, key, str_class):
    copy_source = {
        'Bucket': bucket,
        'Key': key
    }
    response = s3.copy_object(
        CopySource=copy_source,
        Bucket=bucket,
        Key=key,
        StorageClass=str_class
    )
    return response



filename = './obj.csv'

if len(sys.argv) != 3:
    print("Enter arg as script.py bucket list/copy")
    exit()
else:
    BUC = sys.argv[1]
    action = sys.argv[2]
    if action == "list":
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for item in reader:
                key1 = item[1]
                key2 = item[2]
                key3 = item[3]
                key4 = item[4]
                key5 = item[5]
                key6 = item[6]
                key7 = item[7]
                key = f"{key1}/{key2}/{key3}/{key4}/{key5}/{key6}/{key7}/"
                print(key)
                print(list_keys(BUC, key))


    elif action == "copy":
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for item in reader:
                key1 = item[1]
                key2 = item[2]
                key3 = item[3]
                key4 = item[4]
                key5 = item[5]
                key6 = item[6]
                key7 = item[7]
                key = f"{key1}/{key2}/{key3}/{key4}/{key5}/{key6}/{key7}/"
                print(key)
                keys = list_keys(BUC, key)
                print("No. of objects: ", len(keys))
                for i in keys:
                    print(change_str_class(BUC, i, "GLACIER"))

