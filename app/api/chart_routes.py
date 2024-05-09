from flask import Blueprint, jsonify, request, abort
from app.models import *
from datetime import datetime
import json
from app.models.stock_utils.chart_utils import get_barset
from app.models.stock_utils.utils import check_patterns
from sqlalchemy import and_


chart_routes = Blueprint('charts', __name__)

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
    0: '1D',
    1: '1W',
    2: '1M',
    3: '3M',
    4: '1Y',
    5: '5Y',
    6: 'YTD'
}

def get_timeframe_and_barset(id, stock):
    # Check if the id is in the timeframes dictionary
    if id not in timeframes:
        return 'Invalid id', 400, None

    timeframe = timeframes[id]
    barset = get_barset(stock, timeframe)
    json_barset = [bar_to_dict(bar) for bar in barset]
    return timeframe, json_barset

@chart_routes.route('/<int:id>/bars/<int:timeframe>')
def get_stock_bars(id, timeframe):
    stock = Stock.query.get(id)
    timeframe, json_barset = get_timeframe_and_barset(timeframe, stock)
    if timeframe == 'Invalid id':
        return timeframe, 400
    return jsonify(json_barset)

# Timeframes
    # 1: '15Min' 1D
    # 2: '30Min' 1D
    # 3: '1Hour' 1W 1M
    # 4: '1Day' 3M 1Y YTD
    # 5: '1Week' 5Y

pattern_timeframes = {
    '1D' : ['15Min', '30Min'],
    '1W' : ['1Hour'],
    '1M' : ['1Hour'],
    '3M' : ['1Day'],
    '1Y' : ['1Day'],
    '5Y' : ['1Week'],
    'YTD': ['1Day']
}

@chart_routes.route('/<int:id>/patterns/<int:timeframeId>')
def get_stock_patterns_chart(id, timeframeId):
    stock = Stock.query.get(id)
    timeframe = timeframes[timeframeId]
    pattern_timeframe = pattern_timeframes[timeframe]
    patterns = Pattern.query.filter(
    Pattern.stock_id == stock.id,
    Pattern.timeframe.in_(pattern_timeframe)
).all()
    return {'patterns': [pattern.to_dict_stock() for pattern in patterns]}
