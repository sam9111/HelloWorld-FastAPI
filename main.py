from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils import *

app = FastAPI()

origins = ["http://localhost:3000", "localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
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
