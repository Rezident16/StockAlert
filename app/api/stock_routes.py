from flask import Blueprint, jsonify, request, abort
from app.models import *
from datetime import datetime
from app.models.stock_utils.utils import estimate_sentiment, get_barset, check_patterns
import json

stock_routes = Blueprint('stocks', __name__)

@stock_routes.route('/<int:id>')
def get_stock(id):
    stock = Stock.query.get(id)
    return stock.to_dict()

def format_news(news_list):
    formatted_news = []
    for news in news_list:
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


# BARS
def bar_to_dict(bar):
    return {
        'close': bar.c,
        'high': bar.h,
        'low': bar.l,
        'open': bar.o,
        "date": bar.t
    }
@stock_routes.route('/<int:id>/patterns')
def get_stock_patterns(id):
    stock = Stock.query.get(id)
    res = []
    timeframes = ['15Min', '30Min', '1Hour', '1Day', '1Week']
    for time in timeframes:
        barset = get_barset(stock, time)
        json_barset = [bar_to_dict(bar) for bar in barset]
        res.append(check_patterns(json_barset, stock, time))
    return res

@stock_routes.route('/')
def get_all_stocks():
    stocks = Stock.query.all()
    return {"stocks": [stock.to_dict() for stock in stocks]}
