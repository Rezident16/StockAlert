import os
import pickle

import numpy as np
import redis
import talib
from flask import current_app

from ..patterns import Pattern
from ..db import db

DATE_FORMAT = '%Y-%m-%d'

CANDLESTICK_PATTERNS = [
    "CDL2CROWS", "CDL3BLACKCROWS", "CDL3INSIDE", "CDL3LINESTRIKE", "CDL3OUTSIDE",
    "CDL3STARSINSOUTH", "CDL3WHITESOLDIERS", "CDLABANDONEDBABY", "CDLADVANCEBLOCK",
    "CDLBELTHOLD", "CDLBREAKAWAY", "CDLCLOSINGMARUBOZU", "CDLCONCEALBABYSWALL",
    "CDLCOUNTERATTACK", "CDLDARKCLOUDCOVER", "CDLDOJI", "CDLDOJISTAR", "CDLDRAGONFLYDOJI",
    "CDLENGULFING", "CDLEVENINGDOJISTAR", "CDLEVENINGSTAR", "CDLGAPSIDESIDEWHITE",
    "CDLGRAVESTONEDOJI", "CDLHAMMER", "CDLHANGINGMAN", "CDLHARAMI", "CDLHARAMICROSS",
    "CDLHIGHWAVE", "CDLHIKKAKE", "CDLHIKKAKEMOD", "CDLHOMINGPIGEON", "CDLIDENTICAL3CROWS",
    "CDLINNECK", "CDLINVERTEDHAMMER", "CDLKICKING", "CDLKICKINGBYLENGTH", "CDLLADDERBOTTOM",
    "CDLLONGLEGGEDDOJI", "CDLLONGLINE", "CDLMARUBOZU", "CDLMATCHINGLOW", "CDLMATHOLD",
    "CDLMORNINGDOJISTAR", "CDLMORNINGSTAR", "CDLONNECK", "CDLPIERCING", "CDLRICKSHAWMAN",
    "CDLRISEFALL3METHODS", "CDLSEPARATINGLINES", "CDLSHOOTINGSTAR", "CDLSHORTLINE",
    "CDLSPINNINGTOP", "CDLSTALLEDPATTERN", "CDLSTICKSANDWICH", "CDLTAKURI", "CDLTASUKIGAP",
    "CDLTHRUSTING", "CDLTRISTAR", "CDLUNIQUE3RIVER", "CDLUPSIDEGAP2CROWS", "CDLXSIDEGAP3METHODS"
]


class CandlestickPatternDetector:
    """
    Runs TA-Lib's candlestick pattern functions over a bar set, persists any
    newly-seen pattern hits to the DB (emitting a socket event per new hit),
    and uses Redis as a dedup cache so the same pattern/bar combo isn't
    re-inserted on every poll.
    """

    PATTERNS = CANDLESTICK_PATTERNS

    def __init__(self, redis_client=None):
        self.redis = redis_client or redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

    def detect(self, barset, stock, timeframe):
        """Detect + persist new pattern hits for `stock` (a Stock model instance) over `barset` at `timeframe`."""
        from app.sockets.news import patterns_namespace

        open_, high, low, close, date = self._extract_data(barset)
        results = {}

        for pattern in self.PATTERNS:
            result_list = self._run_pattern(pattern, open_, high, low, close)
            hits = self._build_hits(result_list, date, pattern, stock, timeframe, close)

            if not hits:
                continue

            existing = self._get_cached(stock, hits, pattern, timeframe)
            if existing is None:
                pattern_instance = self._build_pattern_instance(stock, hits, pattern, timeframe)
                db.session.add(pattern_instance)
                self._cache(pattern_instance, stock.id, hits[0]['milliseconds'], pattern, hits[0]['sentiment'], timeframe)
                patterns_namespace.emit('patterns', pattern_instance.to_dict_stock(), namespace='/patterns')
            results[pattern] = hits

        db.session.commit()
        return results

    def cache_all(self):
        """Warms the Redis cache from every Pattern row already in the DB. Run on seed."""
        with current_app.app_context():
            for pattern in Pattern.query.all():
                self._cache(pattern, pattern.stock_id, pattern.milliseconds, pattern.pattern_name, pattern.sentiment, pattern.timeframe)

    @staticmethod
    def _extract_data(barset):
        open_ = np.array([bar['open'] for bar in barset]).astype('double')
        high = np.array([bar['high'] for bar in barset]).astype('double')
        low = np.array([bar['low'] for bar in barset]).astype('double')
        close = np.array([bar['close'] for bar in barset]).astype('double')
        date = np.array([bar['date'] for bar in barset])
        return open_, high, low, close, date

    @staticmethod
    def _run_pattern(pattern, open_, high, low, close):
        function = getattr(talib, pattern)
        return function(open_, high, low, close).tolist()

    @staticmethod
    def _build_hits(result_list, date, pattern, stock, timeframe, close):
        hits = []
        for i, value in enumerate(result_list):
            if value >= 100 or value <= -100:
                hits.append({
                    'date': date[i],
                    'milliseconds': CandlestickPatternDetector._to_milliseconds(date[i]),
                    'value': value,
                    'sentiment': 'Bullish' if value >= 100 else 'Bearish',
                    'pattern': pattern,
                    'stock': stock.symbol,
                    'timeframe': timeframe,
                    'close': close[i],
                })
        return hits

    def _get_cached(self, stock, hits, pattern, timeframe):
        key = self._cache_key(stock.id, hits[0]['milliseconds'], pattern, hits[0]['sentiment'], timeframe)
        result = self.redis.get(key)
        return pickle.loads(result) if result else None

    def _cache(self, pattern_instance, stock_id, milliseconds, pattern_name, sentiment, timeframe):
        key = self._cache_key(stock_id, milliseconds, pattern_name, sentiment, timeframe)
        self.redis.set(key, pickle.dumps(pattern_instance))

    @staticmethod
    def _cache_key(stock_id, milliseconds, pattern_name, sentiment, timeframe):
        return f"pattern:{stock_id}:{milliseconds}:{pattern_name}:{sentiment}:{timeframe}"

    @staticmethod
    def _build_pattern_instance(stock, hits, pattern, timeframe):
        return Pattern(
            stock_id=stock.id,
            date=hits[0]['date'].strftime(DATE_FORMAT),
            milliseconds=hits[0]['milliseconds'],
            pattern_name=pattern,
            sentiment=hits[0]['sentiment'],
            value=hits[0]['value'],
            timeframe=timeframe,
            latest_price=hits[0]['close'],
        )

    @staticmethod
    def _to_milliseconds(date_timestamp):
        return int(date_timestamp.to_pydatetime().timestamp() * 1000)
