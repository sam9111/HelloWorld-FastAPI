import json
import os
from datetime import datetime

import pytz
from dotenv import load_dotenv
from newscatcherapi import NewsCatcherApiClient

load_dotenv()

UTC = pytz.utc

newscatcherapi = NewsCatcherApiClient(
    x_api_key=os.getenv("API_KEY")
)  # use 10,000 calls account in production

# Azure Text Analytics Setup
key = os.getenv("AZURE_API_KEY")
endpoint = os.getenv("ENDPOINT")

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credential=ta_credential
    )
    return text_analytics_client


client = authenticate_client()


# Fetching and processing news from NewsCatcherApi


def make_news(response):
    articles = response["articles"]
    news = {"countries": {}, "last_fetched": ""}
    news_by_country = news["countries"]
    for article in articles:
        if article["country"] == "unknown":
            continue
        article_obj = {
            "_id": article["_id"],
            "title": article["title"],
            "summary": article["summary"],
            "topics": article["topic"],
            "published_date": article["published_date"],
            "link": article["link"],
            "country": article["country"],
            "media": article["media"],
        }

        if (country := article["country"]) not in news_by_country:
            country_obj = {"articles": []}
            country_obj["articles"].append(article_obj)
            news_by_country[country] = country_obj
        else:
            if len(news_by_country[country]["articles"]) < 10:
                news_by_country[country]["articles"].append(article_obj)

    news["last_fetched"] = datetime.now(UTC).strftime("%Y:%m:%d %H:%M:%S %Z %z")
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


# Process news to make data with overall sentiments and emotions for each article


def make_data():
    news = get_news()
    news_by_country = news["countries"]
    countries = {}

    for country in news_by_country:
        documents = []
        for article in news_by_country[country]["articles"]:
            documents.append(article["title"])
        responses = client.analyze_sentiment(documents=documents)
        positives = []
        negatives = []
        for response in responses:
            sentiment = response.sentiment
            if sentiment == "neutral":
                continue
            if sentiment == "positive":
                sentiment_score = response.confidence_scores.positive
                positives.append(sentiment_score)
            else:
                sentiment_score = response.confidence_scores.negative
                negatives.append(sentiment_score)

        if len(positives) == 0 and len(negatives) == 0:
            continue
        avg_positive_score = 0
        avg_negative_score = 0
        if len(positives) > 0:
            avg_positive_score = sum(positives) / len(positives)
        if len(negatives) > 0:
            avg_negative_score = sum(negatives) / len(negatives)

        if avg_positive_score > avg_negative_score:
            news_by_country[country]["sentiment"] = "positive"
            news_by_country[country]["sentiment_score"] = avg_positive_score
        else:
            news_by_country[country]["sentiment"] = "negative"
            news_by_country[country]["sentiment_score"] = avg_negative_score
        countries[country] = news_by_country[country]

    news["countries"] = countries
    return news


def update_data():
    with open("data.json", "w") as outfile:
        json.dump(make_data(), outfile)


def get_data():
    update_data()
    with open("data.json", "r") as infile:
        data_json = json.load(infile)
    return data_json


def make_points():
    data = get_data()

    data_by_country = data["countries"]

    with open("countries.json", "r") as infile:
        point_objs = json.load(infile)

    for point_obj in list(point_objs):
        country = point_obj["id"]
        if country not in data_by_country:
            point_objs.remove(point_obj)
            continue

        point_obj["color"] = (
            "green" if data_by_country[country]["sentiment"] == "positive" else "red"
        )

        point_obj["value"] = data_by_country[country]["sentiment_score"] * 100

        point_obj["sentiment"] = data_by_country[country]["sentiment"]

    return point_objs


def update_points():
    with open("points.json", "w") as outfile:
        json.dump(make_points(), outfile)


def get_points():
    with open("points.json", "r") as infile:
        points_json = json.load(infile)
    return points_json
