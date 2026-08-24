import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT = '%Y-%m-%d'
DATA_BASE_URL = 'https://data.alpaca.markets'


class Bar:
    """Mirrors the handful of fields callers read off alpaca_trade_api's Bar objects."""

    __slots__ = ('o', 'h', 'l', 'c', 'v', 't')

    def __init__(self, raw):
        self.o = raw['o']
        self.h = raw['h']
        self.l = raw['l']
        self.c = raw['c']
        self.v = raw.get('v')
        self.t = pd.Timestamp(raw['t'])


class NewsItem:
    """Mirrors the fields callers read off alpaca_trade_api's News objects."""

    def __init__(self, raw):
        self.id = raw['id']
        self.headline = raw.get('headline')
        self.author = raw.get('author')
        self.created_at = pd.Timestamp(raw['created_at'])
        self.summary = raw.get('summary')
        self.url = raw.get('url')
        self.images = raw.get('images')
        self.source = raw.get('source')
        self.symbols = raw.get('symbols', [])


class AlpacaClient:
    """
    Wraps the Alpaca REST API: price bars, snapshots, news, and options
    open interest (used for PCR) - implemented directly with `requests`
    instead of the alpaca_trade_api SDK. That SDK's package __init__
    unconditionally imports its async (aiohttp) and websocket-streaming
    (websockets) submodules even though this app only ever makes plain
    synchronous REST calls - real import weight, likely the cause of the
    import hangs hit during local setup, for functionality never used here.
    """

    # Timeframes used for candlestick pattern detection (matches the labels
    # historically used by stock_routes.py's pattern endpoints). These
    # label strings are already valid Alpaca `timeframe` query values.
    PATTERN_TIMEFRAMES = {
        '15Min': {'timeframe': '15Min', 'limit': 100},
        '30Min': {'timeframe': '30Min', 'limit': 50},
        '1Hour': {'timeframe': '1Hour', 'limit': 750, 'start_key': 'one_month_ago'},
        '1Day': {'timeframe': '1Day', 'limit': 367, 'start_key': 'year_ago'},
        '1Week': {'timeframe': '1Week', 'limit': 264, 'start_key': 'five_year_ago'},
    }

    # Timeframes used by the price chart (matches chart_routes.py's labels).
    CHART_TIMEFRAMES = {
        '1D': {'timeframe': '1Min', 'limit': 1400},
        '1W': {'timeframe': '1Hour', 'limit': 1400, 'start_key': 'one_week_ago', 'needs_end': True},
        '1M': {'timeframe': '1Hour', 'limit': 1400, 'start_key': 'one_month_ago', 'needs_end': True},
        '3M': {'timeframe': '1Day', 'limit': 1400, 'start_key': 'three_month_ago', 'needs_end': True},
        'YTD': {'timeframe': '1Day', 'limit': 1400, 'start_key': 'start_of_year', 'needs_end': True},
        '1Y': {'timeframe': '1Day', 'limit': 1400, 'start_key': 'year_ago', 'needs_end': True},
        '5Y': {'timeframe': '1Week', 'limit': 1400, 'start_key': 'five_year_ago', 'needs_end': True},
    }

    NEWS_PAGE_LIMIT = 50
    NEWS_MAX_RESULTS = 50

    def __init__(self, api_key=None, api_secret=None, base_url=None):
        self.api_key = api_key or os.getenv('API_KEY')
        self.api_secret = api_secret or os.getenv('API_SECRET')
        self.base_url = base_url or os.getenv('BASE_URL')
        self._session = requests.Session()
        self._session.headers.update({
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret,
        })

    @staticmethod
    def get_dates():
        today = datetime.now().date() - timedelta(days=1)
        return {
            'today': today.strftime(DATE_FORMAT),
            'five_days_ago': (today - timedelta(days=5)).strftime(DATE_FORMAT),
            'one_week_ago': (today - timedelta(weeks=1)).strftime(DATE_FORMAT),
            'one_month_ago': (today - relativedelta(months=1)).strftime(DATE_FORMAT),
            'three_month_ago': (today - relativedelta(months=3)).strftime(DATE_FORMAT),
            'start_of_year': datetime(today.year, 1, 1).date().strftime(DATE_FORMAT),
            'year_ago': (today - relativedelta(years=1)).strftime(DATE_FORMAT),
            'five_year_ago': (today - relativedelta(years=5)).strftime(DATE_FORMAT),
        }

    def _get(self, url, params=None, timeout=15):
        response = self._session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def _get_bars(self, symbol, spec):
        dates = self.get_dates()
        base_params = {'timeframe': spec['timeframe']}
        if 'start_key' in spec:
            base_params['start'] = dates[spec['start_key']]
            if spec.get('needs_end'):
                base_params['end'] = dates['today']

        url = f'{DATA_BASE_URL}/v2/stocks/{symbol}/bars'
        bars = []
        page_token = None
        while len(bars) < spec['limit']:
            params = dict(base_params, limit=spec['limit'] - len(bars))
            if page_token:
                params['page_token'] = page_token
            data = self._get(url, params=params)
            # Alpaca returns {"bars": null} (key present, value None), not a
            # missing key, when there's nothing for this symbol/timeframe -
            # dict.get(key, default) only falls back on a missing key.
            bars.extend(Bar(raw) for raw in (data.get('bars') or []))
            page_token = data.get('next_page_token')
            if not page_token:
                break
        return bars

    def get_pattern_bars(self, symbol, timeframe_label):
        spec = self.PATTERN_TIMEFRAMES.get(timeframe_label, self.PATTERN_TIMEFRAMES['1Week'])
        return self._get_bars(symbol, spec)

    def get_chart_bars(self, symbol, timeframe_label):
        spec = self.CHART_TIMEFRAMES[timeframe_label]
        bars = self._get_bars(symbol, spec)
        if not bars and timeframe_label == '1D':
            # '1D' asks for the most recent 1-minute bars with no explicit
            # start date - outside market hours / before today's session
            # has published anything, that legitimately comes back empty.
            # Fall back to the last completed trading day's bars instead of
            # showing nothing.
            fallback_spec = dict(spec, start_key='five_days_ago', needs_end=True)
            bars = self._get_bars(symbol, fallback_spec)
        return bars

    def get_price(self, symbol):
        data = self._get(f'{DATA_BASE_URL}/v2/stocks/{symbol}/snapshot')
        return data['minuteBar']['vw']

    def get_news(self, symbol, start, end):
        url = f'{DATA_BASE_URL}/v1beta1/news'
        articles = []
        page_token = None
        while len(articles) < self.NEWS_MAX_RESULTS:
            params = {
                'symbols': symbol,
                'start': start,
                'end': end,
                'limit': self.NEWS_PAGE_LIMIT,
                'include_content': 'true',
            }
            if page_token:
                params['page_token'] = page_token
            data = self._get(url, params=params)
            articles.extend(NewsItem(raw) for raw in (data.get('news') or []))
            page_token = data.get('next_page_token')
            if not page_token:
                break
        return articles

    def get_put_call_open_interest(self, symbol, expiring_within_days=90):
        """
        Sums put/call open interest across active option contracts on
        `symbol` expiring within `expiring_within_days`. Returns (put_oi, call_oi).
        """
        cutoff = (datetime.now().date() + timedelta(days=expiring_within_days)).strftime(DATE_FORMAT)
        url = f'{self.base_url}/v2/options/contracts'
        put_oi = 0
        call_oi = 0
        page_token = None
        while True:
            params = {
                'underlying_symbols': symbol,
                'expiration_date_lte': cutoff,
                'status': 'active',
                'limit': 1000,
            }
            if page_token:
                params['page_token'] = page_token
            data = self._get(url, params=params)
            for contract in (data.get('option_contracts') or []):
                oi = int(contract.get('open_interest') or 0)
                if contract.get('type') == 'put':
                    put_oi += oi
                elif contract.get('type') == 'call':
                    call_oi += oi
            page_token = data.get('next_page_token')
            if not page_token:
                break
        return put_oi, call_oi
