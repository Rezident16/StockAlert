from datetime import datetime, timedelta
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from dotenv import load_dotenv
import os
from dateutil.relativedelta import relativedelta
from .utils import get_dates

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
}

def get_barset(stock, timeFrameChosen):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    today, one_week_ago, one_month_ago, three_month_ago, start_of_year, year_ago, five_year_ago = get_dates()
    
    if timeFrameChosen == '1D':
        barset = api.get_bars(stock.symbol,timeframe=TimeFrame(1, TimeFrameUnit.Minute), limit=1400)
    elif timeFrameChosen == '1W':
        barset = api.get_bars(stock.symbol,TimeFrame.Hour, start=one_week_ago, end=today, limit=1400)
    elif timeFrameChosen == '1M':
        barset = api.get_bars(stock.symbol,TimeFrame.Hour, start=one_month_ago, end=today, limit=1400)
        # barset = api.get_bars(stock.symbol,timeframe=TimeFrame.Hour, limit=100) # Hourly timeframe
    elif timeFrameChosen == '3M':
        barset = api.get_bars(stock.symbol, TimeFrame.Day, start=three_month_ago, end=today, limit=1400)
    elif timeFrameChosen == 'YTD':
        barset = api.get_bars(stock.symbol, TimeFrame.Day, start=start_of_year, end=today, limit=1400)
    elif timeFrameChosen == '1Y':
        barset = api.get_bars(stock.symbol, TimeFrame.Day, start=year_ago, end=today, limit=1400)
    elif timeFrameChosen == '5Y':
        barset = api.get_bars(stock.symbol, TimeFrame.Week, start=five_year_ago, end=today, limit=1400)
    return barset
