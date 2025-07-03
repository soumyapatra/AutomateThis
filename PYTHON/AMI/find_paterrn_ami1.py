from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import boto3
import re
from datetime import datetime
import dateparser

region = 'ap-southeast-1'
ami_client = boto3.client('ec2', region_name=region)
response = ami_client.describe_images(Owners=['self'])

ami_dict = dict()
ami_names = []
ami_date_dict = dict()


def sortbydate(val):
    return datetime.strptime(val[2], '%d %b %Y')




def sort_ami_by_date(ami_list, date_dict):
    sort_ami_list = []
    
    for ami in ami_list:
        ami_name = ami[0]
        ami += (date_dict[ami_name],)
        sort_ami_list.append(ami)
        sort_ami_list.sort(key=sortbydate)
    return sort_ami_list


# ami_list =[]
for ami in response['Images']:
    ami_dict[ami['Name']] = ami['ImageId']
    parsed_date = dateparser.parse(ami['CreationDate'])
    date = datetime.strftime(parsed_date, '%d %b %Y')
    ami_date_dict[ami['Name']] = date
    ami_names.append(ami['Name'])
    # ami_list.append(tuple([ami['ImageId'],ami['Name'],ami['CreationDate']]))

print(ami_date_dict)

pattern_list = []
for ami_name in ami_names:
    regex1 = '_[0-9]*$'
    regex2 = '-[0-9]*$'
    match = re.search(regex1, ami_name)
    if match is not None:
        pattern = re.sub(regex1, '', ami_name)
    else:
        pattern = re.sub(regex2, '', ami_name)
    if pattern in pattern_list:
        continue
    else:
        pattern_list.append(pattern)
        pattern_search = process.extractBests(pattern, ami_names, score_cutoff=90, limit=400)
        match_num = len(pattern_search)
        sorted_list = sort_ami_by_date(pattern_search, ami_date_dict)
        print(
            f'============================\nami_name:{ami_name}\nPattern_searched:{pattern} \nMatches: {match_num}\nFound Match:{pattern_search}\n=========================\nSorted_list:{sorted_list}\n\n')

