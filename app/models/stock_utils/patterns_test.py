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
import redis
import pickle
from flask import current_app

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
}

api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
DATE_FORMAT = '%Y-%m-%d'

timeframes = {
    1: '15Min',
    2: '30Min',
    3: '1Hour',
    4: '1Day',
    5: '1Week',
}


def get_dates(): 
    today = datetime.now().date() - timedelta(days=1)
    one_week_ago = today - timedelta(weeks=1)
    one_month_ago = today - relativedelta(months=1)
    three_month_ago = today - relativedelta(months=3)
    start_of_year = datetime(today.year, 1, 1).date()
    year_ago = today - relativedelta(years=1)
    five_year_ago = today - relativedelta(years=5)
    return today.strftime(DATE_FORMAT), one_week_ago.strftime(DATE_FORMAT), one_month_ago.strftime(DATE_FORMAT), three_month_ago.strftime(DATE_FORMAT), start_of_year.strftime(DATE_FORMAT), year_ago.strftime(DATE_FORMAT), five_year_ago.strftime(DATE_FORMAT)


def get_barset(stock, timeFrameChosen):
    today, one_week_ago, one_month_ago, three_month_ago, start_of_year, year_ago, five_year_ago = get_dates()
    if timeFrameChosen == '15Min':
        barset = api.get_bars(stock,timeframe=TimeFrame(15, TimeFrameUnit.Minute), limit=100) # 15 Min timeframe
    elif timeFrameChosen == '30Min':
        barset = api.get_bars(stock,timeframe=TimeFrame(30, TimeFrameUnit.Minute), limit=50) # 30 Min timeframe
    elif timeFrameChosen == '1Hour':
        barset = api.get_bars(stock,timeframe=TimeFrame.Hour, start = one_month_ago, limit=750) # Hourly timeframe
    elif timeFrameChosen == '1Day':
        barset = api.get_bars(stock, TimeFrame.Day, start = year_ago , limit=367) # Daily timeframe
    else:
        barset = api.get_bars(stock, TimeFrame.Week, start = five_year_ago, limit=264) # Weekly timeframe
    return barset


pattern = {
    "name": "CDL3INSIDE",
    "sentiment": "bullish",
    "price": 486.41,
    "timeframe": "15Min",
    "milliseconds": 1727701200000
}
def bar_to_dict(bar):
    return {
        'close': round(bar.c, 2),
        'high': round(bar.h, 2),
        'low': round(bar.l,2),
        'open': round(bar.o, 2),
        "date": bar.t,
    }

def convert_date_to_milliseconds(date_timestamp):
    return int(date_timestamp.to_pydatetime().timestamp() * 1000)

date = datetime.fromtimestamp(pattern["milliseconds"] / 1000)
start_date = (date - timedelta(weeks=10)).strftime('%Y-%m-%d')
end_date = (date).strftime('%Y-%m-%d')
# barset = api.get_bars(stock.symbol, TimeFrame.Week, start = five_year_ago, limit=264)
barset = api.get_bars("QQQ", TimeFrame.Week, start=start_date, end=end_date, limit=100)
json_barset = [bar_to_dict(bar) for bar in barset]

local_high = 0


# potential way to calculate the difference between local high and pattern price
# API restricts looking up to "Right now" so we can't get the current price accurately
for bar in json_barset:
    date = bar['date']
    timestamp_milliseconds = convert_date_to_milliseconds(date)
    rand_start = convert_date_to_milliseconds((date - timedelta(weeks=10))) # should be the actual pattern date
    max_time = rand_start + 6048000000 # convert to milliseconds depending on the timeframe * 10
    if timestamp_milliseconds > rand_start and timestamp_milliseconds <= max_time:
        if bar["high"] > local_high:
            local_high = bar["high"]

amount = local_high - json_barset[0]['open']
formatted_amount = "${:.2f}".format(amount)

print(json_barset)
print(formatted_amount)
