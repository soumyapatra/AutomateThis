import configparser
import os
import boto3
import csv

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

with open('rds_recommendation.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(
        ['AccountName', 'ARN', 'InstanceFindings', 'StorageFinding',
         'CurrentInstaceType', 'RecommendedInstanceType', 'RecommendedInstanceTypeRisk'])
    for role in roles:
        acct_name = role.rsplit("-", 1)[0]
        S = " | "
        print(f"working on {role}")
        session = boto3.Session(profile_name=role, region_name="ap-south-1")
        client = session.client('compute-optimizer')
        response = client.get_rds_database_recommendations()
        print(response)
        for recommendation in response['rdsDBRecommendations']:
            inst_findings = recommendation["instanceFinding"]
            str_findings = recommendation["storageFinding"]
            arn = recommendation["resourceArn"]
            current_inst_type = recommendation["currentDBInstanceClass"]
            recommended_inst_type = []
            recommended_inst_type_rank = []
            for option in recommendation["instanceRecommendationOptions"]:
                recommended_inst_type.append(option["dbInstanceClass"])
                recommended_inst_type_rank.append(str(option["rank"]))
            recommended_inst_type_list = S.join(recommended_inst_type)
            recommended_inst_type_rank_list = S.join(recommended_inst_type_rank)
            writer.writerow(
                [acct_name, arn, inst_findings, str_findings, current_inst_type, recommended_inst_type_list,
                 recommended_inst_type_rank_list])

