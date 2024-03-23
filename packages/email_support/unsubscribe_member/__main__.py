import logging
import os

import requests

FUNCTION_NAME = 'cookies_Unsubscribe_member'


def main(event, context):
    key = os.getenv('MAILGUN_API_KEY')
    unsubscribe_member = event.get('unsubscribe_member')
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s {context.activation_id} {FUNCTION_NAME}: %(message)s"
    )
    logging.info(f"Start processing: {unsubscribe_member}")
    r = requests.put(
        "https://api.mailgun.net/v3/lists/sg_law_cookies@mg.your-amicus.app/members/" + unsubscribe_member,
        auth=('api', key),
        data={
            'subscribed': False,
        }
    )
    if r.status_code != 200:
        logging.error(f"Error sending confirmation email: {r.json()['message']}")
