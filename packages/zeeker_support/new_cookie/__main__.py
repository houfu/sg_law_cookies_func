import logging
import os
from datetime import date

import requests
from logtail import LogtailHandler
from pydantic import BaseModel, AnyHttpUrl


class SGLawCookie(BaseModel):
    resource_url: AnyHttpUrl
    cookie_content: str
    published_date: date


def main(event, context):
    handler = LogtailHandler(source_token=os.getenv("LOGTAIL_SOURCE_TOKEN"))
    logger = logging.getLogger(__name__)
    logger.handlers = []
    logger.addHandler(handler)
    logging.basicConfig(
        format=f"%(asctime)s {context.activation_id} {context.function_name}: %(message)s"
    )
    logger.info(f"Start processing event {context.function_name}")
    cookie = SGLawCookie.model_validate_json(event["content"])
    logger.info(f"Validated content: {cookie.resource_url}")
    logger.info(f"Creating resource on CKAN")
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
        logger.info(f"Created resource on CKAN: {response_json['result']['id']}")
        resource_response = requests.post(
            f"https://{os.getenv('ZEEKER_URL')}/api/action/resource_view_create",
            json={
                "resource_id": response_json["result"]["id"],
                "title": "Website view",
                "view_type": "webpage_view",
            },
            headers={
                "Content-Type": "application/json",
                "X-CKAN-API-Key": os.getenv("ZEEKER_API_KEY"),
            },
        )
        resource_response_json = resource_response.json()
    else:
        logger.error(f"Failed to create resource on CKAN: {response_json['error']}")
        return {"body": {"success": False, "error": response_json["error"]}}

    if resource_response_json["success"]:
        # Now add to Datastore
        logger.info(f"Created resource view on CKAN: {response_json['result']['id']}")
        logger.info(f"Creating new entry on Consolidated Datastore")
        datastore_response = requests.post(
            f"https://{os.getenv('ZEEKER_URL')}/api/action/datastore_upsert",
            json={
                "resource_id": "e359c6c3-851a-44a2-ad4d-e319642c0098",
                "method": "insert",
                "force": "True",
                "records": [
                    {
                        "date_published": cookie.published_date.strftime("%d %B %Y"),
                        "title": f"SG Law Cookies ({cookie.published_date.strftime('%d %B %Y')})",
                        "content": cookie.cookie_content,
                        "resource_url": cookie.resource_url,
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
            logger.info(
                f"Successfully added article to datastore: {cookie.resource_url}"
            )
            logger.info(f"{context.function_name} successfully executed")
            return {"body": {"success": True}}
        else:
            logger.error(
                f"[{context.activation_id}] Failed to add article to datastore: {datastore_response_json['error']}"
            )
            return {
                "body": {"success": False, "error": datastore_response_json["error"]}
            }

    else:
        logger.error(f"Failed to create resource view on CKAN: {resource_response_json['error']}")
        return {"body": {"success": False, "error": resource_response_json["error"]}}
