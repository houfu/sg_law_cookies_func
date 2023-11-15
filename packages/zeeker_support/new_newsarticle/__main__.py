import os
import datetime
from typing import Optional

import requests
from pydantic import BaseModel, AnyHttpUrl


class NewsArticle(BaseModel):
    category: str
    title: str
    source_link: AnyHttpUrl
    author: str
    date: datetime.datetime
    summary: Optional[str]


def main(args):
    article = NewsArticle.model_validate_json(args["content"])
    response = requests.post(
        f"https://{os.getenv('ZEEKER_URL')}/api/3/action/datastore_create",
        json={
            "resource": {
                "package_id": "sg-law-cookies-news-items",
                "url": str(article.source_link),
                "description": article.summary,
                "name": article.title,
            },
            "fields": [
                {"id": "date_published", "type": "date"},
                {"id": "summary", "type": "text"},
            ],
            "records": [
                {
                    "date_published": article.date.strftime("%d %B %Y"),
                    "summary": article.summary,
                }
            ],
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": os.getenv("ZEEKER_API_KEY"),
        },
    )
    response_json = response.json()
    print(response_json["success"])
