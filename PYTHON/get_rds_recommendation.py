import json

import boto3
from datetime import datetime

role_name = "xxxxxxxxfin-sbox-role"
region = "ap-south-1"
session = boto3.Session(profile_name=role_name)


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()


def get_rds_recommendation(rds_arn, client_session, region_name):
    client = client_session.client('compute-optimizer', region_name=region_name)
    response = client.get_rds_database_recommendations(resourceArns=[rds_arn],
                                                       recommendationPreferences={
                                                           'cpuVendorArchitectures': ['CURRENT']})
    d = dict()
    d["instance_finding"] = "NA"
    d["storage_finding"] = "NA"
    d["storage_finding_reasoncode"] = "NA"
    d["instance_finding_reasoncode"] = "NA"
    d["recommended_instance_type"] = "NA"
    d["recommended_instance_type_rank"] = "NA"
    if response["rdsDBRecommendations"]:
        recommendation = response["rdsDBRecommendations"][0]
        instance_finding = recommendation["instanceFinding"]
        storage_finding = recommendation["storageFinding"]
        instance_finding_reasoncode = []
        storage_finding_reasoncode = []
        recommended_instance_type = []
        recommended_instance_type_rank = []
        s = "|"
        #print(json.dumps(recommendation, indent=4, default=datetime_converter))
        if "provisioned" in instance_finding:
            d["instance_finding"] = instance_finding
            for option in recommendation["instanceRecommendationOptions"]:
                recommended_instance_type.append(option["dbInstanceClass"])
                recommended_instance_type_rank.append(str(option["rank"]))
            d["recommended_instance_type"] = s.join(recommended_instance_type)
            d["recommended_instance_type_rank"] = s.join(recommended_instance_type_rank)
            for reason in recommendation["instanceFindingReasonCodes"]:
                instance_finding_reasoncode.append(reason)
            d["instance_finding_reasoncode"] = s.join(instance_finding_reasoncode)
        if "provisioned" in storage_finding:
            d["storage_finding"] = storage_finding
            for reason in recommendation["storageFindingReasonCodes"]:
                storage_finding_reasoncode.append(reason)
            d["storage_finding_reasoncode"] = s.join(storage_finding_reasoncode)
        return d
    return d





print(get_rds_recommendation("arn:aws:REDACTED", session, region))
