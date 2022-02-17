import json
import os
from datetime import datetime

import text2emotion as te
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from newscatcherapi import NewsCatcherApiClient

load_dotenv()


newscatcherapi = NewsCatcherApiClient(
    x_api_key=os.getenv("API_KEY")
)  # use 10,000 calls account in production


def make_news(response):
    articles = response["articles"]
    news = {"countries": {}, "last_fetched": ""}
    news_by_country = news["countries"]
    for article in articles:
        if article["country"] == "unknown":
            continue
        article_obj = {
            "title": article["title"],
            "summary": article["summary"],
            "topics": article["topic"],
            "published_date": article["published_date"],
            "link": article["link"],
            "country": article["country"],
            "media": article["media"],
        }

        if (country := article["country"]) not in news_by_country:
            country_obj = {"articles": {}, "total": 1}
            country_obj["articles"][article["_id"]] = article_obj
            news_by_country[country] = country_obj
        else:
            news_by_country[country]["articles"][article["_id"]] = article_obj
            news_by_country[country]["total"] += 1
    news["last_fetched"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    return news


def update_news():
    response = newscatcherapi.get_latest_headlines_all_pages(
        lang="en", when="24h", max_page=1  # remove in production
    )
    with open("news.json", "w") as outfile:
        json.dump(make_news(response), outfile)


def get_news():
    with open("news.json", "r") as infile:
        news_json = json.load(infile)
    return news_json


def process_text(text):
    emotion_obj = te.get_emotion(text)
    emotion_list = sorted(emotion_obj.items(), key=lambda item: item[1], reverse=True)
    if all(value == 0 for value in emotion_list):
        return False
    return list(emotion_list[0])


def make_data():
    news_json = get_news()
    news_by_country = news_json["countries"]
    to_be_deleted = []
    new_obj = {"countries": {}}
    for country in news_by_country:

        articles = news_by_country[country]["articles"]
        emotions = []
        for article_id in articles:
            article_obj = articles[article_id]
            text = article_obj["title"]
            emotion_list = process_text(text)
            if not emotion_list:
                continue
            emotion_list.append(article_id)
            emotions.append(emotion_list)
        emotions.sort(key=lambda x: x[1], reverse=True)
        articles[emotions[0][2]]["top_emotion"] = emotions[0][0]
        new_obj["countries"][country] = {"article": {}}
        new_obj["countries"][country]["article"] = articles[emotions[0][2]]
    return new_obj


def update_data():
    with open("data.json", "w") as outfile:
        json.dump(make_data(), outfile)


def get_data():
    with open("data.json", "r") as infile:
        data_json = json.load(infile)
    return data_json
