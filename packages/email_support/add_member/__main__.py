import os

import requests


def main(args):
    key = os.getenv('MAILGUN_API_KEY')
    new_member = args.get('new_member')
    r = requests.post(
        "https://api.mailgun.net/v3/lists/sg_law_cookies@mg.your-amicus.app/members",
        auth=('api', key),
        data={
            'subscribed': True,
            'address': new_member
        }
    )
    return {
        "body": {
            "message": r.json()['message'],
            "status_code": r.status_code
        }
    }