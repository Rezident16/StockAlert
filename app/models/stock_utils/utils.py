from datetime import datetime, timedelta
# from alpaca_trade_api import REST
from torch import device
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from dotenv import load_dotenv
import talib
import numpy as np
import pytz
import os
from ..patterns import Pattern
from ..news import News
from ..db import db
from ..stock import Stock
import alpaca
import lumibot

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
}
"""
Note: News sentiment analysis.
Utilizing Alpaca API to get news articles for a specific stocqk.
Utilizing torch to analyze the sentiment of the news articles.
"""


"""
Websockets in here currently don't make sense
However, we can potentially run estimate sentiment in the background across all stocks
and emit the news to the frontend when it's done - TODO


"""
def estimate_sentiment(stock):
    # from app import get_socketio
    from app.sockets.news import NewsNameSpace
    # socketio = get_socketio()
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

            for symbol in newsObj['content'].symbols:
                stock = Stock.query.filter_by(symbol=symbol).first()
                """
                Can have muiltiple symbols in the news article that are not necessarily in the db
                We can potentially create these stocks and add them to the db in the future - TODO
                """
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
                        # news_namespace = NewsNameSpace('/news')
                        # news_namespace.emit('news', news_instance.to_dict_stock_news())
        db.session.commit()
    else:
        return 0, labels[-1]     
    return news_and_sentiment


"""
Stock pattern analysis.
Utilizing Alpaca API to get hourly stock data. - Ideally we want to implement multiple timeframe in the future - TODO
"""

def get_dates(prev): 
        today = datetime.now().date() - timedelta(days=1)
        prior = today - timedelta(days=prev + 1)
        prioWeekly = today - timedelta(days=(prev*4))
        return today.strftime('%Y-%m-%d'), prior.strftime('%Y-%m-%d'), prioWeekly.strftime('%Y-%m-%d')

def get_barset(stock, timeFrameChosen):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    # timeframe = TimeFrame.30min
    today, priorDates, prioWeeklyDates = get_dates(30)
    
    if timeFrameChosen == '15Min':
        barset = api.get_bars(stock.symbol,timeframe=TimeFrame(15, TimeFrameUnit.Minute), limit=100) # 15 Min timeframe
    elif timeFrameChosen == '30Min':
        barset = api.get_bars(stock.symbol,timeframe=TimeFrame(30, TimeFrameUnit.Minute), limit=100) # 30 Min timeframe
    elif timeFrameChosen == '1Hour':
        barset = api.get_bars(stock.symbol,timeframe=TimeFrame.Hour, limit=100) # Hourly timeframe
    elif timeFrameChosen == '1Day':
        barset = api.get_bars(stock.symbol, TimeFrame.Day, start=priorDates, end=today, limit=100) # Daily timeframe
    else:
        barset = api.get_bars(stock.symbol, TimeFrame.Week, start=prioWeeklyDates, end=today, limit=100) # Weekly timeframe
    
    # Hourly timeframe
    # Daily timeframe
    """
    Commented out code below. Need to implement a way to track the stock price when the pattern was caught (close price?)
    Track it agains latest price - TODO
    """
    # latest_bar = api.get_latest_bars(stock.symbol)
    # latest_trade = api.get_latest_trade(stock.symbol)
    # latest_bar_price = latest_bar[stock.symbol].vw
    # latest_trade_price = latest_trade.p
    return barset

"""
Adding conversion to milliseconds for the date to avoid adding duplicate patterns.
"""
def convert_date_to_milliseconds(date_timestamp):
    return int(date_timestamp.to_pydatetime().timestamp() * 1000)


"""
Utilizing TA-Lib to check for patterns in the stock data and adding them to the database.
"""
def check_patterns(barset, stock, timeframe):
    from app.sockets.news import patterns_namespace

    open = np.array([bar['open'] for bar in barset])
    high = np.array([bar['high'] for bar in barset])
    low = np.array([bar['low'] for bar in barset])
    close = np.array([bar['close'] for bar in barset])
    date = np.array([bar['date'] for bar in barset])
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
        function = getattr(talib, pattern)
        result = function(open, high, low, close)

        result_list = result.tolist()
        print (result_list, 'result_list')
        bullish_bearish_result = [
            {"date": date[i],"milliseconds": convert_date_to_milliseconds(date[i]), "value": value, "sentiment": 'Bullish', "pattern": pattern, "stock": stock.symbol, 'timeframe': timeframe, 'close': close[i] } if value >= 100 
            else {"date":date[i],"milliseconds": convert_date_to_milliseconds(date[i]), "value": value, "sentiment": 'Bearish', "pattern": pattern, "stock": stock.symbol,'timeframe': timeframe, 'close': close[i]} 
            for i, value in enumerate(result_list) if value >= 100 or value <= -100
        ]

        if len(bullish_bearish_result) > 0:
            existing_pattern = Pattern.query.filter_by(
                stock_id=stock.id,
                milliseconds=bullish_bearish_result[0]['milliseconds'],
                pattern_name=pattern,
                sentiment=bullish_bearish_result[0]['sentiment'],
                timeframe = timeframe
            ).first()

            if existing_pattern is None:
                pattern_instance = Pattern(
                    stock_id=stock.id,
                    date=bullish_bearish_result[0]['date'].strftime('%Y-%m-%d'),
                    milliseconds=bullish_bearish_result[0]['milliseconds'],
                    pattern_name=pattern,
                    sentiment=bullish_bearish_result[0]['sentiment'],
                    value=bullish_bearish_result[0]['value'],
                    timeframe = timeframe,
                    latest_price = bullish_bearish_result[0]['close']
                )
                db.session.add(pattern_instance)
                patterns_namespace.emit('patterns', pattern_instance.to_dict_stock(), namespace='/patterns')
            results[pattern] = bullish_bearish_result
    db.session.commit()
    # return results

def get_price(stock):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    # quotes = api.get_quotes(stock)
    # latest_trade = api.get_latest_trade(stock)
    # latest_quote = api.get_latest_quote(stock)
    snapshot = api.get_snapshot(stock)
    # print(snapshot.minute_bar.vw, 'snapshot')
    return snapshot.minute_bar.vw
