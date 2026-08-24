import os
import time
from datetime import datetime

import redis

from .alpaca_client import AlpacaClient


class PCRSignal:
    """
    Put/call open-interest ratio for a symbol, classified into a sentiment
    tier the way the leveraged-ETF bot's QQQ tracker does, plus a rolling
    10-day trend check (falling PCR vs its own 10-day average = fear
    abating = bullish) borrowed from the main bot's SMH gate. Ported from
    lev_etf_bot.py's _fetch_oi_pcr/_load_pcr and qqq_tracker_bot.py's
    _fetch_pcr (~/Desktop/TradingBotActions/LeveragedETFBot and TestETF) -
    generalized to any symbol instead of being hardcoded to QQQ/SMH. The
    ML confidence gate from that project was intentionally left out.
    """

    FEAR_LEVEL = 1.2       # PCR above this -> fear_contrarian_bullish
    NEUTRAL_LOW = 0.8      # PCR above this -> neutral
    BULLISH_LOW = 0.5      # PCR above this -> slightly_bullish; below -> complacency_contrarian_bearish

    HIGH_OI_CONFIDENCE = 500_000
    MEDIUM_OI_CONFIDENCE = 100_000

    HISTORY_KEY_PREFIX = 'pcr_history'
    HISTORY_WINDOW = 10  # trading days
    HISTORY_RETENTION_DAYS = HISTORY_WINDOW * 3  # how long entries live before being trimmed

    def __init__(self, alpaca_client=None, redis_client=None):
        self.alpaca_client = alpaca_client or AlpacaClient()
        self.redis = redis_client or redis.Redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True
        )

    def evaluate(self, symbol, expiring_within_days=90):
        """Returns a dict describing the current PCR reading for `symbol`, or {'available': False, ...} if it can't be computed."""
        try:
            put_oi, call_oi = self.alpaca_client.get_put_call_open_interest(symbol, expiring_within_days)
        except Exception:
            return {'available': False, 'reason': 'fetch_failed'}

        if call_oi == 0:
            return {'available': False, 'reason': 'no_call_open_interest'}

        pcr = put_oi / call_oi
        sentiment = self._classify(pcr)
        trend = self._record_and_check_trend(symbol, pcr)

        return {
            'available': True,
            'symbol': symbol,
            'pcr': round(pcr, 4),
            'put_open_interest': put_oi,
            'call_open_interest': call_oi,
            'sentiment': sentiment,
            'oi_confidence': self._confidence(put_oi + call_oi),
            'falling_vs_10d_avg': trend,
            'signal': self._to_signal(sentiment, trend),
        }

    def _classify(self, pcr):
        if pcr > self.FEAR_LEVEL:
            return 'fear_contrarian_bullish'
        if pcr > self.NEUTRAL_LOW:
            return 'neutral'
        if pcr > self.BULLISH_LOW:
            return 'slightly_bullish'
        return 'complacency_contrarian_bearish'

    def _confidence(self, total_oi):
        if total_oi > self.HIGH_OI_CONFIDENCE:
            return 'high'
        if total_oi > self.MEDIUM_OI_CONFIDENCE:
            return 'medium'
        return 'low'

    @staticmethod
    def _to_signal(sentiment, falling_vs_10d_avg):
        if sentiment in ('fear_contrarian_bullish', 'slightly_bullish'):
            return 'BUY'
        if sentiment == 'complacency_contrarian_bearish':
            return 'SELL'
        if falling_vs_10d_avg is True:
            return 'BUY'
        return 'NEUTRAL'

    def _record_and_check_trend(self, symbol, pcr):
        """
        Records today's PCR in a Redis sorted set (score = day, member =
        "day:pcr") and reports whether it's below its own 10-day average
        (falling hedging demand). A sorted set makes today's write an
        atomic upsert-by-day (no read-modify-write race on a shared blob
        the way a single JSON value would have), and trimming old entries
        is a range op instead of manual dict pruning. Fails open (returns
        None) until enough history has accumulated.
        """
        key = f'{self.HISTORY_KEY_PREFIX}:{symbol}'
        today = time.strftime('%Y-%m-%d')
        today_score = self._day_score(today)
        cutoff_score = today_score - self.HISTORY_RETENTION_DAYS * 86400

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, today_score, today_score)  # replace any existing entry for today
        pipe.zadd(key, {f'{today}:{pcr}': today_score})
        pipe.zremrangebyscore(key, '-inf', cutoff_score)
        pipe.zrevrangebyscore(key, today_score, '-inf', start=0, num=self.HISTORY_WINDOW)
        *_, recent_members = pipe.execute()

        recent_values = [float(member.rsplit(':', 1)[1]) for member in recent_members]
        if len(recent_values) < self.HISTORY_WINDOW:
            return None
        return pcr < (sum(recent_values) / len(recent_values))

    @staticmethod
    def _day_score(day_str):
        return int(datetime.strptime(day_str, '%Y-%m-%d').timestamp())
