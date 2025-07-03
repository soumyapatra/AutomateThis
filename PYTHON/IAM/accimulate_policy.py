import boto3
import json

# Initialize a session using Amazon IAM
session = boto3.Session()
iam = session.client('iam')

# Constants
ROLE_NAME = 'YourRoleName'
POLICY_SIZE_LIMIT = 6144  # AWS IAM policy size limit in characters


def get_attached_policies(role_name):
    """Retrieve all policies attached to the IAM role."""
    response = iam.list_attached_role_policies(RoleName=role_name)
    return response['AttachedPolicies']


def get_policy_document(policy_arn):
    """Retrieve the policy document for a given policy ARN."""
    response = iam.get_policy(PolicyArn=policy_arn)
    version_id = response['Policy']['DefaultVersionId']
    policy_version = iam.get_policy_version(PolicyArn=policy_arn, VersionId=version_id)
    return policy_version['PolicyVersion']['Document']


def create_policy(policy_name, policy_document):
    """Create a new policy with the given document."""
    response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )
    return response['Policy']['Arn']


def attach_policy(role_name, policy_arn):
    """Attach a policy to the IAM role."""
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)


def main():
    attached_policies = get_attached_policies(ROLE_NAME)
    accumulated_permissions = []
    policy_counter = 1

    for policy in attached_policies:
        policy_arn = policy['PolicyArn']
        policy_document = get_policy_document(policy_arn)
        accumulated_permissions.extend(policy_document['Statement'])

    # Split accumulated permissions into multiple policies if they exceed the size limit
    current_policy_document = {'Version': '2012-10-17', 'Statement': []}
    for statement in accumulated_permissions:
        current_policy_document['Statement'].append(statement)
        if len(json.dumps(current_policy_document)) > POLICY_SIZE_LIMIT:
            # Remove the last statement and create the policy
            current_policy_document['Statement'].pop()
            policy_name = f"{ROLE_NAME}_Policy_{policy_counter}"
            policy_arn = create_policy(policy_name, current_policy_document)
            attach_policy(ROLE_NAME, policy_arn)
            policy_counter += 1
            # Start a new policy document with the last statement
            current_policy_document = {'Version': '2012-10-17', 'Statement': [statement]}

    # Create the last policy if there are remaining statements
    if current_policy_document['Statement']:
        policy_name = f"{ROLE_NAME}_Policy_{policy_counter}"
        policy_arn = create_policy(policy_name, current_policy_document)
        attach_policy(ROLE_NAME, policy_arn)


if __name__ == "__main__":
    main()
