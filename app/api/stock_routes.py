from flask import Blueprint, current_app, jsonify, request, abort
from app.models import *
from app.models.stock_utils.alpaca_client import AlpacaClient
from app.models.stock_utils.sentiment_analyzer import NewsSentimentAnalyzer
from app.models.stock_utils.pattern_detector import CandlestickPatternDetector
from app.models.stock_utils.stock_signal import StockSignal
from app.models.stock_utils.finviz_client import FinvizClient

stock_routes = Blueprint('stocks', __name__)

alpaca_client = AlpacaClient()
sentiment_analyzer = NewsSentimentAnalyzer(alpaca_client)
pattern_detector = CandlestickPatternDetector()
stock_signal = StockSignal(alpaca_client)
finviz_client = FinvizClient()

@stock_routes.route('/<int:id>')
def get_stock(id):
    stock = Stock.query.get(id)
    if stock is None:
        return {'errors': ['Stock not found']}, 404
    return stock.to_dict()

def format_news(news_list):
    formatted_news = []
    for news in news_list:
        if news and 'content' in news:
            content = news['content']
            sentiment = news['sentiment']
            probability = news['probability']
            formatted_content = {
                'author': content.author,
                'headline': content.headline,
                'created_at': content.created_at,
                'sentiment': sentiment,
                'probability': f'{probability:.4f}',
                'url': content.url,
                'images': content.images,
                'summary': content.summary,
                'source': content.source,
                'symbols': content.symbols,
                'id': content.id,
            }
            formatted_news.append(formatted_content)
    return formatted_news

@stock_routes.route('/<int:id>/news')
def get_stock_news(id):
    news_items = News.query.filter_by(stock_id=id).all()
    news = [news_item.to_dict_self() for news_item in news_items]
    return jsonify(news)


# Fetches + stores news for all stocks. Runs FinBERT sentiment inference
# synchronously per stock, so it's slow - prefer `flask stocks refresh-news`
# on a schedule over hitting this route directly.
def refresh_all_news():
    all_news = []
    stocks = Stock.query.all()
    for stock in stocks:
        news = sentiment_analyzer.analyze(stock)
        all_news.extend(format_news(news))
    return all_news

@stock_routes.route('/news')
def get_all_news():
    return jsonify(refresh_all_news())


# FINVIZ DATA
@stock_routes.route("/<int:id>/finviz_stock_data")
def get_finviz_stock_data(id):
    stock = Stock.query.get(id)
    if stock is None:
        return {'errors': ['Stock not found']}, 404
    stock_data = finviz_client.get_stock_data(stock.symbol)
    return jsonify(stock_data)

# Gets the price of the stock in real time
@stock_routes.route('/<int:id>/stock_price')
def get_stock_price(id):
    stock = Stock.query.get(id)
    if stock is None:
        return {'errors': ['Stock not found']}, 404
    price = alpaca_client.get_price(stock.symbol)
    return jsonify(price)

# Read-only BUY/SELL/NEUTRAL signal for the stock (trend + momentum + PCR).
@stock_routes.route('/<int:id>/signal')
def get_stock_signal(id):
    stock = Stock.query.get(id)
    if stock is None:
        return {'errors': ['Stock not found']}, 404
    return jsonify(stock_signal.evaluate(stock.symbol))

# BARS
def bar_to_dict(bar):
    return {
        'close': round(bar.c, 2),
        'high': round(bar.h, 2),
        'low': round(bar.l,2),
        'open': round(bar.o, 2),
        "date": bar.t,
    }

timeframes = {
    1: '15Min',
    2: '30Min',
    3: '1Hour',
    4: '1Day',
    5: '1Week',
}

def get_timeframe_and_barset(id, stock):
    if id not in timeframes:
        return 'Invalid id', 400, None

    timeframe = timeframes[id]
    barset = alpaca_client.get_pattern_bars(stock.symbol, timeframe)
    json_barset = [bar_to_dict(bar) for bar in barset]
    return timeframe, json_barset

# Detects + stores candlestick patterns for all stocks at one timeframe.
# Fetches bars from Alpaca and runs TA-Lib per stock, so it's slow - prefer
# `flask stocks refresh-patterns` on a schedule over hitting this route directly.
def refresh_all_patterns(timeframe_id):
    stocks = Stock.query.all()
    res = []
    for stock in stocks:
        result = get_timeframe_and_barset(timeframe_id, stock)
        if result[0] == 'Invalid id':
            break
        timeframe, json_barset = result[0], result[1]
        res.append(pattern_detector.detect(json_barset, stock, timeframe))
    return res

@stock_routes.route('/get_patterns/<int:id>')
def get_stocks_patterns(id):
    return refresh_all_patterns(id)

# Get patterns per stock
@stock_routes.route('/<int:id>/patterns')
def get_stock_patterns(id):
    stock = Stock.query.get(id)
    if stock is None:
        return {'errors': ['Stock not found']}, 404
    patterns = Pattern.query.filter_by(stock_id=stock.id).all()
    return {'patterns': [pattern.to_dict_stock() for pattern in patterns]}


@stock_routes.route('/')
def get_all_stocks():
    stocks = Stock.query.all()
    return {"stocks": [stock.to_dict() for stock in stocks]}
