from flask import Blueprint, jsonify, request, abort
from app.models import *
from datetime import datetime
from app.models.stock_utils.utils import estimate_sentiment, get_barset, check_patterns, get_price
import json
stock_routes = Blueprint('stocks', __name__)

@stock_routes.route('/<int:id>')
def get_stock(id):
    stock = Stock.query.get(id)
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
    stock = Stock.query.get(id)
    news = estimate_sentiment(stock)
    formatted_news = format_news(news)
    return jsonify(formatted_news)
    # return stock.to_dict()

@stock_routes.route('/news')
def get_all_news():
    all_news = []
    stocks = Stock.query.all()
    for stock in stocks:
        news = estimate_sentiment(stock)
        formatted_news = format_news(news)
        all_news.append(formatted_news)
    return jsonify([n.to_dict_self() for n in all_news])

@stock_routes.route('/<int:id>/stock_price')
def get_stock_price(id):
    stock = Stock.query.get(id)
    price = get_price(stock.symbol)
    return jsonify(price)

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
    5: '15Min',
    4: '30Min',
    3: '1Hour',
    2: '1Day',
    1: '1Week',
}

def get_timeframe_and_barset(id, stock):
    if id not in timeframes:
        return 'Invalid id', 400, None

    timeframe = timeframes[id]
    barset = get_barset(stock, timeframe)
    json_barset = [bar_to_dict(bar) for bar in barset]
    return timeframe, json_barset

@stock_routes.route('/get_patterns/<int:id>')
def get_stocks_patterns(id):
    stocks = Stock.query.all()
    res = []
    for stock in stocks:
        timeframe, json_barset = get_timeframe_and_barset(id, stock)
        if timeframe == 'Invalid id':
            return timeframe, 400
        res.append(check_patterns(json_barset, stock, timeframe))


@stock_routes.route('/<int:id>/patterns')
def get_stock_patterns(id):
    stock = Stock.query.get(id)
    patterns = Pattern.query.filter_by(stock_id=stock.id).all()
    return {'patterns': [pattern.to_dict_stock() for pattern in patterns]}
    # return jsonify(res)


@stock_routes.route('/')
def get_all_stocks():
    stocks = Stock.query.all()
    return {"stocks": [stock.to_dict() for stock in stocks]}
