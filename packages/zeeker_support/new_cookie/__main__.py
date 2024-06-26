import logging
import os
from datetime import date

import requests
from pydantic import BaseModel, AnyHttpUrl

FUNCTION_NAME = "New_Cookie"


class SGLawCookie(BaseModel):
    resource_url: AnyHttpUrl
    cookie_content: str
    published_date: date


def main(event, context):
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s {context.activation_id} {FUNCTION_NAME}: %(message)s",
    )
    logging.info(f"Start processing event {context.function_name}")
    cookie = SGLawCookie.model_validate_json(event["content"])
    logging.info(f"Validated content: {cookie.resource_url}")
    logging.info(f"Creating resource on CKAN")
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
        logging.info(f"Created resource on CKAN: {response_json['result']['id']}")
        resource_response = requests.get(
            f"https://n8n.zeeker.sg/webhook-test/446306a8-99a1-42b1-bda1-657df38efb17",
            params={
                "resource": response_json['result']['id']
            }
        )
        resource_response_json = resource_response.json()
    else:
        logging.error(f"Failed to create resource on CKAN: {response_json['error']}")
        return {"body": {"success": False, "error": response_json["error"]}}

    if resource_response_json["success"]:
        # Now add to Datastore
        logging.info(f"Created resource view on CKAN: {response_json['result']['id']}")
        logging.info(f"Creating new entry on Consolidated Datastore")
        datastore_response = requests.post(
            f"https://{os.getenv('ZEEKER_URL')}/api/action/datastore_upsert",
            json={
                "resource_id": "f89215de-9770-41e7-ab80-4fe6993cb91f",
                "method": "insert",
                "force": "True",
                "records": [
                    {
                        "date_published": cookie.published_date.strftime("%d %B %Y"),
                        "title": f"SG Law Cookies ({cookie.published_date.strftime('%d %B %Y')})",
                        "content": cookie.cookie_content,
                        "resource_url": str(cookie.resource_url),
                    },
                ],
            },
            headers={
                "Content-Type": "application/json",
                "X-CKAN-API-Key": os.getenv("ZEEKER_API_KEY"),
            },
        )
        datastore_response_json = datastore_response.json()
        if datastore_response_json["success"]:
            logging.info(
                f"Successfully added article to datastore: {cookie.resource_url}"
            )
            logging.info(f"{context.function_name} successfully executed")
            return {"body": {"success": True}}
        else:
            logging.error(
                f"[{context.activation_id}] Failed to add article to datastore: {datastore_response_json['error']}"
            )
            return {
                "body": {"success": False, "error": datastore_response_json["error"]}
            }

    else:
        logging.error(
            f"Failed to create resource view on CKAN: {resource_response_json['error']}"
        )
        return {"body": {"success": False, "error": resource_response_json["error"]}}
