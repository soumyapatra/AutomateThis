import boto3

def get_instance_tag(region, search_tag,  search_tag_val,  target_tag):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_iterator = ec2.instances.filter(Filters=[{'Name': 'tag-key', 'Values': [search_tag, target_tag]}])
    tags_list = []
    for instance in instance_iterator:
        tags = instance.tags
        for tag in tags:
            if tag["Key"] == search_tag and tag["Value"] in search_tag_val:
                for tag in tags:
                    if tag["Key"] == target_tag and tag["Value"] not in tags_list:
                        tags_list.append(tag["Value"] )
    return tags_list
    
tags = get_instance_tag("ap-south-1",  "billing_unit",  ["gr_rc_production", "gr_reverie_production"],  "Application")
print(tags)
                
                
    
