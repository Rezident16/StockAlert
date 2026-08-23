import numpy as np
import talib

from ..patterns import Pattern
from ..db import db

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
    Runs TA-Lib's candlestick pattern functions over a bar set and persists
    any newly-seen pattern hits to the DB (emitting a socket event per new
    hit). Dedup is one indexed query against the `patterns` table - backed
    by a DB-level unique constraint on (stock_id, pattern_name, sentiment,
    timeframe, milliseconds) - rather than a separate Redis cache. That
    used to be the *only* dedup check (nothing here ever queried the DB),
    so a flushed/restarted Redis would silently start re-inserting
    duplicates; a single indexed SELECT is both simpler and strictly
    correct, so there's no second source of truth to keep in sync.
    """

    PATTERNS = CANDLESTICK_PATTERNS

    def detect(self, barset, stock, timeframe):
        """Detect + persist new pattern hits for `stock` (a Stock model instance) over `barset` at `timeframe`."""
        from app.sockets.news import patterns_namespace

        open_, high, low, close, date = self._extract_data(barset)
        results = {}
        existing = self._existing_keys(stock.id, timeframe)

        for pattern in self.PATTERNS:
            result_list = self._run_pattern(pattern, open_, high, low, close)
            hits = self._build_hits(result_list, date, pattern, stock, timeframe, close)

            if not hits:
                continue

            key = (pattern, hits[0]['sentiment'], hits[0]['milliseconds'])
            if key not in existing:
                pattern_instance = self._build_pattern_instance(stock, hits, pattern, timeframe)
                db.session.add(pattern_instance)
                existing.add(key)
                patterns_namespace.emit('patterns', pattern_instance.to_dict_stock(), namespace='/patterns')
            results[pattern] = hits

        db.session.commit()
        return results

    @staticmethod
    def _existing_keys(stock_id, timeframe):
        rows = Pattern.query.with_entities(
            Pattern.pattern_name, Pattern.sentiment, Pattern.milliseconds
        ).filter_by(stock_id=stock_id, timeframe=timeframe).all()
        return {(name, sentiment, ms) for name, sentiment, ms in rows}

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

    @staticmethod
    def _build_pattern_instance(stock, hits, pattern, timeframe):
        return Pattern(
            stock=stock,
            date=hits[0]['date'].to_pydatetime(),
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
