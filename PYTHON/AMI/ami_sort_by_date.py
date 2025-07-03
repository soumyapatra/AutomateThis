import boto3
import dateparser
from datetime import datetime

ami_list = [{'ami_name': 'prod_rc_fe_payment_service_201906041258', 'ami_id': 'ami-035767986def4785a',
             'ami_date': '04 Jun 2019'},
            {'ami_name': 'prod_rc_fe_payment_service_201808141126', 'ami_id': 'ami-059a502eb951b83ef',
             'ami_date': '14 Aug 2018'},
            {'ami_name': 'prod_rc_fe_payment_service_201906171022', 'ami_id': 'ami-067194011001ce1d2',
             'ami_date': '17 Jun 2019'},
            {'ami_name': 'prod_rc_fe_payment_service_201905300856', 'ami_id': 'ami-09f9dc87ae0b894c1',
             'ami_date': '30 May 2019'}]

ami_list1 = [{'ami_date': '04 Jun 2019'}, {'ami_date': '14 Aug 2018'}, {'ami_date': '17 Jun 2019'},
             {'ami_date': '30 May 2019'}]


def list_slice(list1):
    sliced_list = list1[: len(list1) - 3]
    return sliced_list


ami_list1 = sorted(ami_list1,key=lambda x: datetime.strptime(x["ami_date"], "%d %b %Y"))

ami_list1 = list_slice(ami_list1)
print(ami_list1)
