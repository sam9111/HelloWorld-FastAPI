from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from utils import *
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/news")
def news():
    return get_news()


@app.get("/api/data")
def data():
    return get_data()


@app.get("/api/points")
def points():
    return get_points()


def update():
    update_news()
    logger.info("Finished updating news")
    update_data()
    logger.info("Finished updating data")
    update_points()
    logger.info("Finished updating points")


@app.on_event("startup")
def update_loop():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update, "cron", hour=23)
    scheduler.start()
