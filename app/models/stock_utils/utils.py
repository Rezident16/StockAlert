from datetime import datetime, timedelta
from torch import device
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from dateutil.relativedelta import relativedelta
import torch
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from dotenv import load_dotenv
import talib
import numpy as np
import os
from ..patterns import Pattern
from ..news import News
from ..stock import Stock
from ..db import db
import redis
import pickle
from flask import current_app


### Use for sentiment analysis on a news article ###
# Set the device to "cuda:0" if CUDA is available, otherwise use the CPU
# 
# device = "cuda:0" if torch.cuda.is_available() else "cpu"
device = "mps" if torch.backends.mps.is_available() else ("cuda:0" if torch.cuda.is_available() else "cpu")

# Using Transformers to analize news sentiment
# https://huggingface.co/yiyanghkust/finbert-tone
finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer, device=device)



# Create a connection to a local Redis database
r = redis.Redis(host='localhost', port=6379, db=0)

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
}

api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)


# NEWS FUNCTIONS

DATE_FORMAT = '%Y-%m-%d'

# Main function to fetch the news and estimate the sentiment
# @stock_routes.route('/news') used to fetch al news to all stocks + estimate sentiment
def estimate_sentiment(stock):
    news = fetch_news(stock)
    if not news:
        return 0, "Neutral"
    news_and_sentiment = estimate_news_sentiment(news)
    store_news_in_db(news_and_sentiment)
    return news_and_sentiment

# Fetch news from the Alpaca API
def fetch_news(stock):
    today = datetime.now().date()
    week_prior = today - timedelta(days=7)
    return api.get_news(stock.symbol, end=today.strftime(DATE_FORMAT), start=week_prior.strftime(DATE_FORMAT), include_content=True)

# Estimate the sentiment and probability of the news with finbert
def estimate_news_sentiment(news):
    news_and_sentiment = []
    for text in news:
        content = text.summary if text.summary else text.headline

        """
        Text has content available which need to be parsed with beautifulsoup
        Content may contain information about other stocks as well,
        need to figure out how to analyze it properly to give accurate sentiment to the user.
        Potential solution:
        1. Check if the content can be properly split into segments (unlikely)
        2. Analize each segment seperately and give sentiment to each paragraph
        3. Check if there is a specific HTML tag that splits the content into different sections
        4. Beautiful soup to split into paragraphs. If paragraph has a mention of a stock, analyze it - 
        requires to change stock model to include stock name (TSLA) -> Tesla - check news_test.py 
        """
        
        # content = text.content if text.content else (text.summary if text.summary else text.headline)
        result = nlp(content)
        probability = result[0]["score"]
        sentiment = result[0]["label"]
        newsObj = {
            "content": text,
            "probability": probability,
            "sentiment": sentiment
        }
        news_and_sentiment.append(newsObj)
    return news_and_sentiment


# Store news in the db per each stock available in the db
def store_news_in_db(news_and_sentiment):
    from app.sockets.news import news_namespace
    for newsObj in news_and_sentiment:
        for symbol in newsObj['content'].symbols:
            stock = Stock.query.filter_by(symbol=symbol).first()
            if stock:
                existing_news = News.query.filter_by(
                    news_id=newsObj['content'].id, 
                    stock_id=stock.id).first()

                if existing_news is None:
                    news_instance = add_news_to_db(newsObj, stock)
                    news_namespace.emit('news', news_instance.to_dict_stock_news(), namespace='/news')
    db.session.commit()

# Add news to the db session
def add_news_to_db(newsObj, stock):
    news_instance = News(
        news_id=newsObj['content'].id,
        stock_id=stock.id,
        author=newsObj['content'].author,
        headline=newsObj['content'].headline,
        created_at=str(newsObj['content'].created_at),
        sentiment = newsObj['sentiment'],
        probability = newsObj['probability'],
        url=newsObj['content'].url,
        images=newsObj['content'].images,
        source=newsObj['content'].source,
        summary=newsObj['content'].summary,
        symbols = newsObj['content'].symbols
    )
    db.session.add(news_instance)
    return news_instance



# PATTERN FUNCTIONS
"""
Need to implement the function to calculate success rate:
Potential solution:
Compare the "price when caught" against the local high/low (5-10 bars)
15 Min: 150Mins range
30 Min: 300Mins range
1 Hour: 600Mins range
1 Day: 10 Days range
1 Week: 10 Weeks range
Would potentially need to update pattern model or create new for success - continuesly would be modified
    while within local range
For the specific pattern (Name, Timeframe, Sentiment, maybe stock as well) - continue to add count,
    difference against local high/low, and update the average
"""


PATTERNS = [
    "CDL2CROWS", "CDL3BLACKCROWS", "CDL3INSIDE", "CDL3LINESTRIKE", "CDL3OUTSIDE",
    "CDL3STARSINSOUTH", "CDL3WHITESOLDIERS", "CDLABANDONEDBABY", "CDLADVANCEBLOCK",
    "CDLBELTHOLD", "CDLBREAKAWAY", "CDLCLOSINGMARUBOZU", "CDLCONCEALBABYSWALL",
    "CDLCOUNTERATTACK", "CDLDARKCLOUDCOVER", "CDLDOJI", "CDLDOJISTAR", "CDLDRAGONFLYDOJI",
    "CDLENGULFING", "CDLEVENINGDOJISTAR", "CDLEVENINGSTAR", "CDLGAPSIDESIDEWHITE",
    "CDLGRAVESTONEDOJI", "CDLHAMMER", "CDLHANGINGMAN", "CDLHARAMI", "CDLHARAMICROSS",
    "CDLHIGHWAVE", "CDLHIKKAKE", "CDLHIKKAKEMOD", "CDLHOMINGPIGEON", "CDLIDENTICAL3CROWS",
    "CDLINNECK", "CDLINVERTEDHAMMER", "CDLKICKING", "CDLKICKINGBYLENGTH", "CDLLADDERBOTTOM",
    "CDLLONGLEGGEDDOJI", "CDLLONGLINE", "CDLMARUBOZU", "CDLMATCHINGLOW", "CDLMATHOLD",
    "CDLMORNINGDOJISTAR", "CDLMORNINGSTAR", "CDLONNECK", "CDLPIERCING", "CDLRICKSHAWMAN",
    "CDLRISEFALL3METHODS", "CDLSEPARATINGLINES", "CDLSHOOTINGSTAR", "CDLSHORTLINE",
    "CDLSPINNINGTOP", "CDLSTALLEDPATTERN", "CDLSTICKSANDWICH", "CDLTAKURI", "CDLTASUKIGAP",
    "CDLTHRUSTING", "CDLTRISTAR", "CDLUNIQUE3RIVER", "CDLUPSIDEGAP2CROWS", "CDLXSIDEGAP3METHODS"
]

def get_dates(): 
    today = datetime.now().date() - timedelta(days=1)
    one_week_ago = today - timedelta(weeks=1)
    one_month_ago = today - relativedelta(months=1)
    three_month_ago = today - relativedelta(months=3)
    start_of_year = datetime(today.year, 1, 1).date()
    year_ago = today - relativedelta(years=1)
    five_year_ago = today - relativedelta(years=5)
    return today.strftime(DATE_FORMAT), one_week_ago.strftime(DATE_FORMAT), one_month_ago.strftime(DATE_FORMAT), three_month_ago.strftime(DATE_FORMAT), start_of_year.strftime(DATE_FORMAT), year_ago.strftime(DATE_FORMAT), five_year_ago.strftime(DATE_FORMAT)

# Get the barset for a specific stock and timeframe
# Used by stock routes to get the barset for the stock
def get_barset(stock, timeFrameChosen):
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

# Commit to session the paterns that don't exist in the database. Emit to the FE
# @stock_routes.route('/get_patterns/<int:id>') always runs to check for patterns
def check_patterns(barset, stock, timeframe):
    from app.sockets.news import patterns_namespace
    # Convert the barset into numpy arrays
    # Current barset is a list of dictionaries with keys: open, high, low, close, date
    open, high, low, close, date = extract_data(barset)
    results = {}

    for pattern in PATTERNS:
        # Check if pattern is present with TA-LIB
        result_list = check_pattern(pattern, open, high, low, close)

        # Convert the results into a list of dictionaries
        bullish_bearish_result = create_results(result_list, date, pattern, stock, timeframe, close)

        if len(bullish_bearish_result) > 0:
            # Check if the pattern already exists in the database via cache
            existing_pattern = query_existing_pattern(stock, bullish_bearish_result, pattern, timeframe)

            # If the pattern does not exist, create a new pattern instance and cache it
            if existing_pattern is None:
                pattern_instance = create_pattern_instance(stock, bullish_bearish_result, pattern, timeframe)
                db.session.add(pattern_instance)
                cache_pattern(pattern_instance, stock.id, bullish_bearish_result[0]['milliseconds'], pattern, bullish_bearish_result[0]['sentiment'], timeframe)
                patterns_namespace.emit('patterns', pattern_instance.to_dict_stock(), namespace='/patterns')
            results[pattern] = bullish_bearish_result
    db.session.commit()

# Used to get the price of a stock
def get_price(stock):
    snapshot = api.get_snapshot(stock)
    return snapshot.minute_bar.vw

# Runs when seeding the db
def cache_all_patterns():
    with current_app.app_context(): #necessary for querying the database with Pattern.query.all()
        all_patterns = Pattern.query.all()
        for pattern in all_patterns:
            cache_pattern(pattern, pattern.stock_id, pattern.milliseconds, pattern.pattern_name, pattern.sentiment, pattern.timeframe)

# Helper Functions

def extract_data(barset):
    open = np.array([bar['open'] for bar in barset]).astype('double')
    high = np.array([bar['high'] for bar in barset]).astype('double')
    low = np.array([bar['low'] for bar in barset]).astype('double')
    close = np.array([bar['close'] for bar in barset]).astype('double')
    date = np.array([bar['date'] for bar in barset])
    return open, high, low, close, date


# Check the pattern with TA-LIB
def check_pattern(pattern, open, high, low, close):
    function = getattr(talib, pattern) # Get the function from TA-LIB
    result = function(open, high, low, close)
    return result.tolist()

# Create the results for the patterns turning them into dictionaries
def create_results(result_list, date, pattern, stock, timeframe, close):
    return [
        {"date": date[i],"milliseconds": convert_date_to_milliseconds(date[i]), "value": value, "sentiment": 'Bullish', "pattern": pattern, "stock": stock.symbol, 'timeframe': timeframe, 'close': close[i] } if value >= 100 
        else {"date":date[i],"milliseconds": convert_date_to_milliseconds(date[i]), "value": value, "sentiment": 'Bearish', "pattern": pattern, "stock": stock.symbol,'timeframe': timeframe, 'close': close[i]} 
        for i, value in enumerate(result_list) if value >= 100 or value <= -100
    ]

# Query the cache for the pattern - check if it exists
def query_existing_pattern(stock, bullish_bearish_result, pattern, timeframe):
    key = generate_cache_key(stock.id, bullish_bearish_result[0]['milliseconds'], pattern, bullish_bearish_result[0]['sentiment'], timeframe)
    result = r.get(key)
    return pickle.loads(result) if result else None

def create_pattern_instance(stock, bullish_bearish_result, pattern, timeframe):
    return Pattern(
        stock_id=stock.id,
        date=bullish_bearish_result[0]['date'].strftime(DATE_FORMAT),
        milliseconds=bullish_bearish_result[0]['milliseconds'],
        pattern_name=pattern,
        sentiment=bullish_bearish_result[0]['sentiment'],
        value=bullish_bearish_result[0]['value'],
        timeframe = timeframe,
        latest_price = bullish_bearish_result[0]['close']
    )

# Needed to cache new patterns
def cache_pattern(pattern_instance, stock_id, milliseconds, pattern_name, sentiment, timeframe):
    key = generate_cache_key(stock_id, milliseconds, pattern_name, sentiment, timeframe)
    r.set(key, pickle.dumps(pattern_instance))

# Generate unique key for the cache per pattern
def generate_cache_key(stock_id, milliseconds, pattern_name, sentiment, timeframe):
    return f"pattern:{stock_id}:{milliseconds}:{pattern_name}:{sentiment}:{timeframe}"

def convert_date_to_milliseconds(date_timestamp):
    return int(date_timestamp.to_pydatetime().timestamp() * 1000)
