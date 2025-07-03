import argparse
import sys

import pdpyras


def get_users(session):
    #    sys.stdout.write("Listing All Users' Contact Methods:\n")
    sys.stdout.write("Name,Email,Phone,Push,Sms")
    for user in session.iter_all('users'):
        name = user['name']
        id = user['id']
        email = get_contact_methods_new(id, session, 'email')
        phone = get_contact_methods_new(id, session, 'phone')
        push = get_contact_methods_new(id, session, 'push_notification')
        sms = get_contact_methods_new(id, session, 'sms')
        print(f'{name}, {email}, {phone}, {push}, {sms}')


def get_contact_methods_new(user_id, session, method):
    for contact_method in session.iter_all('users/%s/contact_methods' % user_id):
        if method in contact_method['type']:
            if method == "email":
                address = contact_method['address']
                return f'Email: {address}'
            elif method == "phone":
                cont_code = contact_method['country_code']
                address = contact_method['address']
                return f'Phone: {cont_code} {address}'
            elif method == "push_notification":
                label = contact_method['label']
                return f'Push: {label}'
            elif method == "sms":
                cont_code = contact_method['country_code']
                address = contact_method['address']
                return f'SMS: {cont_code} {address}'
    return "NA"


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Retrieves contact info for all "
                                             "users in a PagerDuty account")
    ap.add_argument('-k', '--api-key', required=True, help="REST API key")
    args = ap.parse_args()
    session = pdpyras.APISession(args.api_key)
    get_users(session)
