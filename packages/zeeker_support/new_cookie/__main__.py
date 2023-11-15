import os
from datetime import date

import requests
from pydantic import BaseModel, AnyHttpUrl


class SGLawCookie(BaseModel):
    resource_url: AnyHttpUrl
    cookie_content: str
    published_date: date


def main(args):
    cookie = SGLawCookie.model_validate_json(args["content"])
    response = requests.post(
        f"https://{os.getenv('ZEEKER_URL')}/api/3/action/datastore_create",
        json={
            "resource": {
                "package_id": "sg-law-cookies",
                "url": str(cookie.resource_url),
                "description": f"SG Law Cookies, an algorithmically produced digest of legal news in Singapore, "
                f"for {cookie.published_date.strftime('%d %B %Y')}",
                "name": f"SG Law Cookies ({cookie.published_date.strftime('%d %B %Y')})"
            },
            "fields": [
                {"id": "date_published", "type": "date"},
                {"id": "content", "type": "text"},
            ],
            "records": [
                {
                    "date_published": cookie.published_date.strftime("%d %B %Y"),
                    "content": cookie.cookie_content,
                }
            ],
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": os.getenv("ZEEKER_API_KEY"),
        },
    )
    response_json = response.json()
    print(response_json['success'])
