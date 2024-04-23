from flask import Blueprint, jsonify, request, abort
from app.models import *
from datetime import datetime
from app.models.stock_utils.news import estimate_sentiment

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

@stock_routes.route('/')
def get_all_stocks():
    stocks = Stock.query.all()
    return {"stocks": [stock.to_dict() for stock in stocks]}
