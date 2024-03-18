import os

import requests

address = "sg_law_cookies@mg.your-amicus.app"


def main(event, context):
    print(f"[{context.activation_id}] Start processing event {context.function_name}")
    key = os.getenv('MAILGUN_API_KEY')
    title = event.get('title')
    content_html = event.get('content_html')
    content_text = event.get('content_text')
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
    print(f"[{context.activation_id}] Response: {r.status_code} {r.json()}")
    print(f"[{context.activation_id}] End processing event {context.function_name}")
    return {
        "body": {
            "message": r.json()['message'],
            "status_code": r.status_code
        }
    }
