import hashlib
import logging
import os

import requests

FUNCTION_NAME = 'cookies_add_member'


def main(event, context):
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s {context.activation_id} {FUNCTION_NAME}: %(message)s"
    )
    key = os.getenv('MAILGUN_API_KEY')
    new_member = event.get('new_member')
    logging.info(f"Start processing: {new_member}")
    hash_arg = event.get('hash')
    salted_email = "cookies" + new_member
    salted_email_bytes = salted_email.encode("utf-8")
    hash_object = hashlib.sha256(salted_email_bytes)
    hash_hex = hash_object.hexdigest()
    if hash_hex != hash_arg:
        raise Exception('Member does not check. Unauthorised.')
    r = requests.post(
        "https://api.mailgun.net/v3/lists/sg_law_cookies@mg.your-amicus.app/members",
        auth=('api', key),
        data={
            'subscribed': True,
            'address': new_member
        }
    )
    if r.status_code == 200:
        logging.info(f"Member {new_member} subscribed to SG Law Cookies")
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
    else:
        logging.error(f"Error subscribing to SG Law Cookies: {r.json()['message']}")
