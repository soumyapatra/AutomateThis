import boto3
import json
from datetime import datetime

region = "ap-south-1"
session = boto3.Session(profile_name="xxxxxxxxfin-sbox-role")
client = session.client('compute-optimizer', region_name="ap-south-1")


def get_instance_recommendation(instance_arn, session, region_name):
    client = session.client('compute-optimizer', region_name=region_name)
    recommendation_preferences = {
        'cpuVendorArchitectures': ['CURRENT']
    }
    response = client.get_ec2_instance_recommendations(instanceArns=[instance_arn],
                                                       recommendationPreferences=recommendation_preferences)
    if response['instanceRecommendations']:
        recommendation = response["instanceRecommendations"][0]
        if recommendation["finding"] == "OVER_PROVISIONED" and len(recommendation["recommendationOptions"]) > 0:
            d = dict()
            current_instance_type = recommendation["currentInstanceType"]
            recommend_instance_types = []
            recommend_instance_ranks = []
            recommend_migration_effort = []
            # print(instance_name, current_instance_type)
            # json_dump = json.dumps(recommendation, indent=4, default=datetime_converter)
            for instance_recommendation in recommendation["recommendationOptions"]:
                if instance_recommendation["instanceType"] != current_instance_type:
                    recommend_instance_types.append(instance_recommendation["instanceType"])
                    recommend_instance_ranks.append(str(instance_recommendation["rank"]))
                    recommend_migration_effort.append(instance_recommendation["migrationEffort"])
            # print(current_instance_type,recommend_instance_types)
            s = "|"
            recommend_instance_types_string = s.join(recommend_instance_types)
            recommend_instance_ranks_string = s.join(recommend_instance_ranks)
            recommend_migration_effort_string = s.join(recommend_migration_effort)
            d["instance_types"] = recommend_instance_types_string
            d["instance_ranks"] = recommend_instance_ranks_string
            d["migration_effort"] = recommend_migration_effort_string
            d["finding"] = recommendation["finding"]
            return d
        else:
            return "NA"


print(get_instance_recommendation("arn:aws:REDACTED", session, region))