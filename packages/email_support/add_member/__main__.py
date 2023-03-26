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
    if r.status_code == 200:
        requests.post(
            "https://api.mailgun.net/v3/mg.your-amicus.app/messages",
            auth=("api", key),
            data={
                "from": "SG Law Cookies by Your Amicus <cookies@your-amicus.app>",
                "to": new_member,
                "subject": "Thanks for subscribing to SG Law Cookies",
                "template": "welcome_sg_cookies"
            }
        )
    return {
        "body": {
            "message": r.json()['message'],
            "status_code": r.status_code
        }
    }