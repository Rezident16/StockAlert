from .db import db, environment, SCHEMA, add_prefix_for_prod
# Import libraries
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import date
import time
import urllib.request
from timedelta import Timedelta 
from datetime import datetime

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple
from alpaca_trade_api import REST
from dotenv import load_dotenv

import os
device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]


load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
    "PAPER": True
}

def get_response(url):
    while True:
        try:
            response = urllib.request.urlopen(url)
            return response
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5) 
            else:
                raise 

class Stock(db.Model):
    __tablename__ = 'stocks'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)

    watchlist_stocks = db.relationship('WatchlistStock', back_populates='stock', cascade='all, delete-orphan')



    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
        }
    
    def to_dict_watchlist(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
        }



    def estimate_sentiment(self):
        print (self)
        api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        today = datetime.now().date()
        three_days_prior = today - Timedelta(days=3)
        news = api.get_news(self.symbol, end=today.strftime('%Y-%m-%d'), start=three_days_prior.strftime('%Y-%m-%d'))
        news_and_sentiment = []
        if news:
            for text in news:
                content = text.__dict__["_raw"]["headline"]
                tokens = tokenizer(content, return_tensors="pt", padding=True).to(device)

                result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])[
                    "logits"
                ]
                result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
                probability = result[torch.argmax(result)]
                sentiment = labels[torch.argmax(result)]
                # print(probability, sentiment, "probability and sentiment")
                newsObj = {}
                newsObj["content"] = text
                newsObj["probability"] = probability
                newsObj["sentiment"] = sentiment
                news_and_sentiment.append(newsObj)
                # text.probability = probability
                # text.sentiment = sentiment
        else:
            return 0, labels[-1]     
        return news_and_sentiment
