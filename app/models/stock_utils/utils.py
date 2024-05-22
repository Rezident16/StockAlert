from datetime import datetime, timedelta
from torch import device
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from dotenv import load_dotenv
import talib
import numpy as np
import os
from ..patterns import Pattern
from ..news import News
from ..db import db
from ..stock import Stock
from dateutil.relativedelta import relativedelta
import redis
import pickle
from flask import current_app


device = "cuda:0" if torch.cuda.is_available() else "cpu"
r = redis.Redis(host='localhost', port=6379, db=0)

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
}
def fetch_news(stock):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    today = datetime.now().date()
    week_prior = today - timedelta(days=7)
    return api.get_news(stock.symbol, end=today.strftime('%Y-%m-%d'), start=week_prior.strftime('%Y-%m-%d'))

def estimate_news_sentiment(news):
    news_and_sentiment = []
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
    return news_and_sentiment

def store_news_in_db(news_and_sentiment):
    from app.sockets.news import news_namespace
    for newsObj in news_and_sentiment:
        for symbol in newsObj['content'].symbols:
            stock = Stock.query.filter_by(symbol=symbol).first()
            if stock:
                existing_news = News.query.filter_by(
                    news_id=newsObj['content'].id, 
                    stock_id = stock.id).first()

                if existing_news is None:
                    news_instance = News(
                        news_id=newsObj['content'].id,
                        stock_id=stock.id,
                        author=newsObj['content'].author,
                        headline=newsObj['content'].headline,
                        created_at=str(newsObj['content'].created_at),
                        sentiment=newsObj['sentiment'].tolist() if isinstance(newsObj['sentiment'], torch.Tensor) else newsObj['sentiment'],
                        probability=newsObj['probability'].tolist() if isinstance(newsObj['probability'], torch.Tensor) else newsObj['probability'],
                        url=newsObj['content'].url,
                        images=newsObj['content'].images,
                        source=newsObj['content'].source,
                        summary=newsObj['content'].summary
                    )
                    db.session.add(news_instance)
                    news_namespace.emit('news', news_instance.to_dict_stock_news(), namespace='/news')
    db.session.commit()

def estimate_sentiment(stock):
    news = fetch_news(stock)
    if not news:
        return 0, labels[-1]
    news_and_sentiment = estimate_news_sentiment(news)
    store_news_in_db(news_and_sentiment)
    return news_and_sentiment

def get_dates(): 
    today = datetime.now().date() - timedelta(days=1)
    one_week_ago = today - timedelta(weeks=1)
    one_month_ago = today - relativedelta(months=1)
    three_month_ago = today - relativedelta(months=3)
    start_of_year = datetime(today.year, 1, 1).date()
    year_ago = today - relativedelta(years=1)
    five_year_ago = today - relativedelta(years=5)
    return today.strftime('%Y-%m-%d'), one_week_ago.strftime('%Y-%m-%d'), one_month_ago.strftime('%Y-%m-%d'), three_month_ago.strftime('%Y-%m-%d'), start_of_year.strftime('%Y-%m-%d'), year_ago.strftime('%Y-%m-%d'), five_year_ago.strftime('%Y-%m-%d')
    

def get_barset(stock, timeFrameChosen):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    today, one_week_ago, one_month_ago, three_month_ago, start_of_year, year_ago, five_year_ago = get_dates()
    if timeFrameChosen == '15Min':
        barset = api.get_bars(stock.symbol,timeframe=TimeFrame(15, TimeFrameUnit.Minute), limit=100) # 15 Min timeframe
    elif timeFrameChosen == '30Min':
        barset = api.get_bars(stock.symbol,timeframe=TimeFrame(30, TimeFrameUnit.Minute), limit=50) # 30 Min timeframe
    elif timeFrameChosen == '1Hour':
        barset = api.get_bars(stock.symbol,timeframe=TimeFrame.Hour, start = one_month_ago, limit=750) # Hourly timeframe
    elif timeFrameChosen == '1Day':
        barset = api.get_bars(stock.symbol, TimeFrame.Day, start = year_ago , limit=367) # Daily timeframe
    else:
        barset = api.get_bars(stock.symbol, TimeFrame.Week, start = five_year_ago, limit=264) # Weekly timeframe
    return barset


def convert_date_to_milliseconds(date_timestamp):
    return int(date_timestamp.to_pydatetime().timestamp() * 1000)


def extract_data(barset):
    open = np.array([bar['open'] for bar in barset]).astype('double')
    high = np.array([bar['high'] for bar in barset]).astype('double')
    low = np.array([bar['low'] for bar in barset]).astype('double')
    close = np.array([bar['close'] for bar in barset]).astype('double')
    date = np.array([bar['date'] for bar in barset])
    return open, high, low, close, date

def check_pattern(pattern, open, high, low, close):
    function = getattr(talib, pattern)
    result = function(open, high, low, close)
    return result.tolist()

def create_results(result_list, date, pattern, stock, timeframe, close):
    return [
        {"date": date[i],"milliseconds": convert_date_to_milliseconds(date[i]), "value": value, "sentiment": 'Bullish', "pattern": pattern, "stock": stock.symbol, 'timeframe': timeframe, 'close': close[i] } if value >= 100 
        else {"date":date[i],"milliseconds": convert_date_to_milliseconds(date[i]), "value": value, "sentiment": 'Bearish', "pattern": pattern, "stock": stock.symbol,'timeframe': timeframe, 'close': close[i]} 
        for i, value in enumerate(result_list) if value >= 100 or value <= -100
    ]

def cache_all_patterns():
    with current_app.app_context():
        # Query all patterns from the database
        all_patterns = Pattern.query.all()

        for pattern in all_patterns:
            # Create a unique key for each pattern
            key = f"pattern:{pattern.stock_id}:{pattern.milliseconds}:{pattern.pattern_name}:{pattern.sentiment}:{pattern.timeframe}"

            # Store the pattern in Redis
            r.set(key, pickle.dumps(pattern))
def query_existing_pattern(stock, bullish_bearish_result, pattern, timeframe):
    key = f"pattern:{stock.id}:{bullish_bearish_result[0]['milliseconds']}:{pattern}:{bullish_bearish_result[0]['sentiment']}:{timeframe}"
    result = r.get(key)

    if result is not None:
        return pickle.loads(result)
    else:
        r.set(key, pickle.dumps(result))
        return result

def create_pattern_instance(stock, bullish_bearish_result, pattern, timeframe):
    return Pattern(
        stock_id=stock.id,
        date=bullish_bearish_result[0]['date'].strftime('%Y-%m-%d'),
        milliseconds=bullish_bearish_result[0]['milliseconds'],
        pattern_name=pattern,
        sentiment=bullish_bearish_result[0]['sentiment'],
        value=bullish_bearish_result[0]['value'],
        timeframe = timeframe,
        latest_price = bullish_bearish_result[0]['close']
    )

def check_patterns(barset, stock, timeframe):
    from app.sockets.news import patterns_namespace

    open, high, low, close, date = extract_data(barset)

    patterns = [
        "CDL2CROWS",
        "CDL3BLACKCROWS",
        "CDL3INSIDE",
        "CDL3LINESTRIKE",
        "CDL3OUTSIDE",
        "CDL3STARSINSOUTH",
        "CDL3WHITESOLDIERS",
        "CDLABANDONEDBABY",
        "CDLADVANCEBLOCK",
        "CDLBELTHOLD",
        "CDLBREAKAWAY",
        "CDLCLOSINGMARUBOZU",
        "CDLCONCEALBABYSWALL",
        "CDLCOUNTERATTACK",
        "CDLDARKCLOUDCOVER",
        "CDLDOJI",
        "CDLDOJISTAR",
        "CDLDRAGONFLYDOJI",
        "CDLENGULFING",
        "CDLEVENINGDOJISTAR",
        "CDLEVENINGSTAR",
        "CDLGAPSIDESIDEWHITE",
        "CDLGRAVESTONEDOJI",
        "CDLHAMMER",
        "CDLHANGINGMAN",
        "CDLHARAMI",
        "CDLHARAMICROSS",
        "CDLHIGHWAVE",
        "CDLHIKKAKE",
        "CDLHIKKAKEMOD",
        "CDLHOMINGPIGEON",
        "CDLIDENTICAL3CROWS",
        "CDLINNECK",
        "CDLINVERTEDHAMMER",
        "CDLKICKING",
        "CDLKICKINGBYLENGTH",
        "CDLLADDERBOTTOM",
        "CDLLONGLEGGEDDOJI",
        "CDLLONGLINE",
        "CDLMARUBOZU",
        "CDLMATCHINGLOW",
        "CDLMATHOLD",
        "CDLMORNINGDOJISTAR",
        "CDLMORNINGSTAR",
        "CDLONNECK",
        "CDLPIERCING",
        "CDLRICKSHAWMAN",
        "CDLRISEFALL3METHODS",
        "CDLSEPARATINGLINES",
        "CDLSHOOTINGSTAR",
        "CDLSHORTLINE",
        "CDLSPINNINGTOP",
        "CDLSTALLEDPATTERN",
        "CDLSTICKSANDWICH",
        "CDLTAKURI",
        "CDLTASUKIGAP",
        "CDLTHRUSTING",
        "CDLTRISTAR",
        "CDLUNIQUE3RIVER",
        "CDLUPSIDEGAP2CROWS",
        "CDLXSIDEGAP3METHODS"
    ]
    results = {}
    for pattern in patterns:
        result_list = check_pattern(pattern, open, high, low, close)
        bullish_bearish_result = create_results(result_list, date, pattern, stock, timeframe, close)

        if len(bullish_bearish_result) > 0:
            existing_pattern = query_existing_pattern(stock, bullish_bearish_result, pattern, timeframe)

            if existing_pattern is None:
                pattern_instance = create_pattern_instance(stock, bullish_bearish_result, pattern, timeframe)
                db.session.add(pattern_instance)
                key = f"pattern:{stock.id}:{bullish_bearish_result[0]['milliseconds']}:{pattern}:{bullish_bearish_result[0]['sentiment']}:{timeframe}"
                r.set(key, pickle.dumps(pattern_instance))
                patterns_namespace.emit('patterns', pattern_instance.to_dict_stock(), namespace='/patterns')
            results[pattern] = bullish_bearish_result
            
    db.session.commit()

def get_price(stock):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    snapshot = api.get_snapshot(stock)
    return snapshot.minute_bar.vw
