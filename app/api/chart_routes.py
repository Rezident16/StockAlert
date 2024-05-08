from flask import Blueprint, jsonify, request, abort
from app.models import *
from datetime import datetime
import json
from app.models.stock_utils.chart_utils import get_barset


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
