import asyncio
import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from newscatcherapi import NewsCatcherApiClient

import utils

load_dotenv()

app = FastAPI()

origins = ["http://localhost:3000", "localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


newscatcherapi = NewsCatcherApiClient(
    x_api_key=os.getenv("API_KEY")
)  # use 10,000 calls account in production


def make_data(response):
    articles = response["articles"]
    news = {"countries": {}, "last_fetched": ""}
    news_by_country = news["countries"]
    for article in articles:
        if article["country"] == "unknown":
            continue
        article_obj = {
            "id": article["_id"],
            "title": article["title"],
            "summary": article["summary"],
            "topics": article["topic"],
            "published_date": article["published_date"],
            "link": article["link"],
            "country": article["country"],
            "media": article["media"],
        }

        if (country := article["country"]) not in news_by_country:
            country_obj = {"articles": [article_obj], "total": 1}
            news_by_country[country] = country_obj
        else:
            news_by_country[country]["articles"].append(article_obj)
            news_by_country[country]["total"] += 1
    news["last_fetched"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    return news


def update_data():
    response = newscatcherapi.get_latest_headlines_all_pages(
        lang="en", when="24h", max_page=1  # remove in production
    )

    with open("news.json", "w") as outfile:
        json.dump(make_data(response), outfile)


def get_data():
    with open("news.json", "r") as infile:
        data = json.load(infile)
    return data


@app.get("/")
def news():
    return get_data()
