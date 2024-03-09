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
    # Create resource
    response = requests.post(
        f"https://{os.getenv('ZEEKER_URL')}/api/action/resource_create",
        json={
            "package_id": "sg-law-cookies",
            "url": str(cookie.resource_url),
            "description": f"SG Law Cookies, an algorithmically produced digest of legal news in Singapore, "
            f"for {cookie.published_date.strftime('%d %B %Y')}",
            "name": f"SG Law Cookies ({cookie.published_date.strftime('%d %B %Y')})",
            "format": "HTML",
        },
        headers={
            "Content-Type": "application/json",
            "X-CKAN-API-Key": os.getenv("ZEEKER_API_KEY"),
        },
    )
    response_json = response.json()
    # If resource is created, create a view
    if response_json["success"]:
        resource_response = requests.post(
            f"https://{os.getenv('ZEEKER_URL')}/api/action/resource_view_create",
            json={
                "resource_id": response_json,
                "title": "Website view",
                "view_type": "webpage_view",
            },
            headers={
                "Content-Type": "application/json",
                "X-CKAN-API-Key": os.getenv("ZEEKER_API_KEY"),
            },
        )
        resource_response_json = resource_response.json()
        print(resource_response_json["success"])
    else:
        print(False)
