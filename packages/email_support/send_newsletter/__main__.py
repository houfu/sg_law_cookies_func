import os

import requests

address = "sg_law_cookies@mg.your-amicus.app"


def main(args):
    key = os.getenv('MAILGUN_API_KEY')
    title = args.get('title')
    content_html = args.get('content_html')
    content_text = args.get('content_text')
    r = requests.post(
        "https://api.mailgun.net/v3/mg.your-amicus.app/messages",
        auth=("api", key),
        data={
            "from": "SG Law Cookies by Your Amicus <cookies@your-amicus.app>",
            "to": address,
            "subject": title,
            "html": content_html,
            "text": content_text
        }
    )
    return {
        "body": {
            "message": r.json()['message'],
            "status_code": r.status_code
        }
    }
