from flask import Blueprint, jsonify, request, abort
from app.models import *
from datetime import datetime

stock_routes = Blueprint('stocks', __name__)

@stock_routes.route('/<int:id>')
def get_stock(id):
    stock = Stock.query.get(id)
    return stock.to_dict()

@stock_routes.route('/<int:id>/news')
def get_stock_news(id):
    stock = Stock.query.get(id)
    news = stock.estimate_sentiment()
    return str(news)
