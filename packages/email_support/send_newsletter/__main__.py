import logging
import os

import requests
from logtail import LogtailHandler

address = "sg_law_cookies@mg.your-amicus.app"


def main(event, context):
    handler = LogtailHandler(source_token=os.getenv("LOGTAIL_SOURCE_TOKEN"))
    logger = logging.getLogger(__name__)
    logger.handlers = []
    logger.addHandler(handler)
    logging.basicConfig(
        format=f"%(asctime)s {context.activation_id} {context.function_name}: %(message)s"
    )
    logger.info(f"Start processing event {context.function_name}")
    key = os.getenv("MAILGUN_API_KEY")
    title = event.get("title")
    content_html = event.get("content_html")
    content_text = event.get("content_text")
    r = requests.post(
        "https://api.mailgun.net/v3/mg.your-amicus.app/messages",
        auth=("api", key),
        data={
            "from": "SG Law Cookies by Your Amicus <cookies@your-amicus.app>",
            "to": address,
            "subject": title,
            "html": content_html,
            "text": content_text,
        },
    )
    logger.info(f"Response: {r.status_code} {r.json()}")
    logger.info(f"End processing event {context.function_name}")
    return {"body": {"message": r.json()["message"], "status_code": r.status_code}}
