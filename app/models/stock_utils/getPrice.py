
# from alpaca_trade_api import REST
from alpaca_trade_api import REST
from dotenv import load_dotenv
import os


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

def get_price(stock):
    api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
    snapshot = api.get_snapshot(stock)
    return snapshot.minute_bar.vw
