from flask import Blueprint, current_app, jsonify, request, abort
from app.models import *
from app.models.stock_utils.utils import estimate_sentiment, get_barset, check_patterns, get_price
from app.models.stock_utils.finvizHelper import get_finviz_data

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

# Needs to be modified - we are already getting the news in the get_all_news function
# Might need to modify the model to include symbols
# Done

# @stock_routes.route('/<int:id>/news')
# def get_stock_news(id):
#     stock = Stock.query.get(id)
#     news = estimate_sentiment(stock)
#     formatted_news = format_news(news)
#     return jsonify(formatted_news)



@stock_routes.route('/<int:id>/news')
def get_stock_news(id):
    news_items = News.query.filter_by(stock_id=id).all()
    news = [news_item.to_dict_self() for news_item in news_items]
    return jsonify(news)


# Continuesly Runs to get all news for all stocks
@stock_routes.route('/news')
def get_all_news():
    all_news = []
    stocks = Stock.query.all()
    for stock in stocks:
        news = estimate_sentiment(stock)
        formatted_news = format_news(news)
        all_news.append(formatted_news)
    if not all_news:
        return jsonify([])
    else:
        return jsonify([n.to_dict_self() for n in all_news])


# FINVIZ DATA
@stock_routes.route("/<int:id>/finviz_stock_data")
def get_finviz_stock_data(id):
    stock = Stock.query.get(id)
    symbol = stock.symbol
    stock_data = get_finviz_data(symbol)
    return jsonify(stock_data)




# Gets the price of the stock in real time
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
    barset = get_barset(stock, timeframe)
    json_barset = [bar_to_dict(bar) for bar in barset]
    return timeframe, json_barset

# Runs Always to continuesly create stock patterns
@stock_routes.route('/get_patterns/<int:id>')
def get_stocks_patterns(id):
    stocks = Stock.query.all()
    res = []
    for stock in stocks:
        result = get_timeframe_and_barset(id, stock)
        if result[0] == 'Invalid id':
            break
        timeframe, json_barset = result[0], result[1]
        res.append(check_patterns(json_barset, stock, timeframe))
    return res

# Get patterns per stock
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
