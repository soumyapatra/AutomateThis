import boto3

profile_name = "lazypay-prod-role"
region = "ap-south-1"


def get_cloudformation_stacks(role):
    session = boto3.Session(profile_name=role,region_name=region)
    client = session.client('cloudformation')
    paginator = client.get_paginator('describe_stacks')
    stacks = []
    for page in paginator.paginate():
        stacks.extend(page['Stacks'])
    return stacks


def get_template_bucket(stack):
    if 'TemplateURL' in stack:
        template_url = stack['TemplateURL']
        if template_url.startswith('https://s3.amazonaws.com/'):
            bucket_name = template_url.split('/')[3]
            return bucket_name
    return None


def main():
    stacks = get_cloudformation_stacks(profile_name)
    for stack in stacks:
        stack_name = stack['StackName']
        bucket_name = get_template_bucket(stack)
        if bucket_name:
            print(f'Stack: {stack_name}, Template Bucket: {bucket_name}')
        else:
            print(f'Stack: {stack_name}, Template Bucket: Not found or not using S3')


if __name__ == '__main__':
    main()
