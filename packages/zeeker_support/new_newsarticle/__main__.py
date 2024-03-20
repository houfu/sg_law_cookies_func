import datetime
import logging
import os
from logging.handlers import SysLogHandler

import requests
from pydantic import BaseModel, AnyHttpUrl


class NewsArticle(BaseModel):
    category: str
    title: str
    source_link: AnyHttpUrl
    author: str
    date: datetime.datetime
    summary: str
    text: str


def main(event, context):
    logger = logging.getLogger()
    logger.addHandler(SysLogHandler())
    logging.basicConfig(
        format=f"%(asctime)s {context.activation_id} {context.function_name}: %(message)s"
    )
    logger.info(f"Start processing event {context.function_name}")
    article = NewsArticle.model_validate_json(event["content"])
    logger.info(f"Validated content: {article.category} {article.title}")
    logger.info(f"Creating resource on CKAN")
    response = requests.post(
        f"https://{os.getenv('ZEEKER_URL')}/api/action/resource_create",
        json={
            "package_id": "sg-law-news-articles",
            "url": str(article.source_link),
            "description": article.summary,
            "name": article.title,
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
        logger.info(f"Created resource view on CKAN: {response_json['result']['id']}")
        logger.info(f"Creating new entry on Consolidated Datastore")
        datastore_response = requests.post(
            f"https://{os.getenv('ZEEKER_URL')}/api/action/datastore_upsert",
            json={
                "resource_id": "df662817-7d40-438a-ba5f-f6e5e23e9454",
                "method": "insert",
                "force": "True",
                "records": [
                    {
                        "date_published": article.date.strftime("%d %B %Y"),
                        "title": article.title,
                        "content": article.text,
                        "author": article.author,
                        "summary": article.summary,
                        "category": article.category,
                        "resource_url": article.source_link,
                        "zeeker_url": f"https://ckan.zeeker.sg/dataset/sg-law-news-articles/resource/"
                        f"{response_json['result']['id']}",
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
            logger.info(f"Successfully added article to datastore: {article.title}")
            logger.info(f"{context.function_name} successfully executed")
            return {"body": {"success": True}}
        else:
            logger.error(
                f"Failed to add article to datastore: {datastore_response_json['error']}"
            )
            return {
                "body": {"success": False, "error": datastore_response_json["error"]}
            }
    else:
        logger.error(
            f"Failed to create resource view: {resource_response_json['error']}"
        )
        return {"body": {"success": False, "error": resource_response_json["error"]}}
