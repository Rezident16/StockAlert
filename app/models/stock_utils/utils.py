from datetime import datetime, timedelta
# from alpaca_trade_api import REST
from torch import device
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from dotenv import load_dotenv
import urllib.request
import time

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

def estimate_sentiment(stock):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    news = api.get_news(stock.symbol, end=today.strftime('%Y-%m-%d'), start=yesterday.strftime('%Y-%m-%d'))
    news_and_sentiment = []
    if news:
        for text in news:
            content = text.__dict__["_raw"]["headline"]
            tokens = tokenizer(content, return_tensors="pt", padding=True).to(device)

            result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])["logits"]
            result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
            probability = result[torch.argmax(result)]
            sentiment = labels[torch.argmax(result)]
            newsObj = {}
            newsObj["content"] = text
            newsObj["probability"] = probability
            newsObj["sentiment"] = sentiment
            news_and_sentiment.append(newsObj)
    else:
        return 0, labels[-1]     
    return news_and_sentiment


def get_barset(stock):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    timeframe = TimeFrame.Hour
    barset = api.get_bars(stock.symbol, timeframe, limit=10)
    print (barset)
    return barset
