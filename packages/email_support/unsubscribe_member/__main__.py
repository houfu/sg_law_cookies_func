import hashlib
import os

import requests


def main(args):
    key = os.getenv('MAILGUN_API_KEY')
    unsubscribe_member = args.get('unsubscribe_member')
    r = requests.put(
        "https://api.mailgun.net/v3/lists/sg_law_cookies@mg.your-amicus.app/members/" + unsubscribe_member,
        auth=('api', key),
        data={
            'subscribed': False,
        }
    )
    return {
        "body": {
            "message": r.json()['message'],
            "status_code": r.status_code
        }
    }