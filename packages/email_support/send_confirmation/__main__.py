import hashlib
import json
import os
from urllib.parse import urlencode

import requests


def main(args):
    key = os.getenv('MAILGUN_API_KEY')
    new_member: str = args.get('new_member')
    salted_email = "cookies" + new_member
    salted_email_bytes = salted_email.encode("utf-8")
    hash_object = hashlib.sha256(salted_email_bytes)
    hash_hex = hash_object.hexdigest()
    confirm_link = "http://cookies.your-amicus.app/subscribe/?" + urlencode({'new_member': new_member, 'hash': hash_hex})
    r = requests.post(
        "https://api.mailgun.net/v3/mg.your-amicus.app/messages",
        auth=("api", key),
        data={
            "from": "SG Law Cookies by Your Amicus <cookies@your-amicus.app>",
            "to": new_member,
            "subject": "Confirm your subscription to SG Law Cookies",
            "template": "confirm-email",
            "t:variables": json.dumps({"confirm_link": confirm_link})
        }
    )
    return {
        "body": {
            "message": r.json()['message'],
            "status_code": r.status_code
        }
    }
