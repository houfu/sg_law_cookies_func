import hashlib
import json
import logging
import os
from urllib.parse import urlencode

import requests

FUNCTION_NAME = 'cookies_send_confirmation'


def main(event, context):
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s {context.activation_id} {FUNCTION_NAME}: %(message)s"
    )
    key = os.getenv('MAILGUN_API_KEY')
    new_member: str = event.get('new_member')
    logging.info(f"Start processing: {new_member}")
    salted_email = "cookies" + new_member
    salted_email_bytes = salted_email.encode("utf-8")
    hash_object = hashlib.sha256(salted_email_bytes)
    hash_hex = hash_object.hexdigest()
    confirm_link = ("https://cookies.your-amicus.app/subscribe/?"
                    + urlencode({'new_member': new_member, 'hash': hash_hex}))
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
    if r.status_code != 200:
        logging.error(f"Error sending confirmation email: {r.json()['message']}")
