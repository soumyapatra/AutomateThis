import boto3

f = open('/tmp/instance_details.csv', 'w')
f.write(f'ID,NAME,TEAM,APPLICATION,PRIVATE_IP,INSTANCE_TYPE\n')
f.close()


def get_instance_details(tagkey, tagvalue=""):
    ec2 = boto3.resource('ec2')
    f = open('/tmp/instance_details.csv', 'a')
    FILTER = [{'Name': f'tag:{tagkey}', 'Values': [f'{tagvalue}']}]
    instance_list = list(ec2.instances.filter(Filters=FILTER))
    for instance in instance_list:
        name = "NA"
        team = "NA"
        app = "NA"
        for tag in instance.tags:
            if tag['Key'] == "Name":
                name = tag['Value']
                name = name.replace(",", "-")
            elif tag['Key'] == "Team":
                team = tag['Value']
                team = team.replace(",", "-")
            elif tag['Key'] == "Application":
                app = tag['Value']
                app = app.replace(",", "-")
        id = instance.id
        ip = instance.private_ip_address
        type = instance.instance_type
        f.write(f'{id},{name},{team},{app},{ip},{type}\n')
    f.close()


get_instance_details('pf_tp')
get_instance_details('pf_app')
