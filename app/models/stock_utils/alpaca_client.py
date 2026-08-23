import os
from datetime import datetime, timedelta

import requests
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT = '%Y-%m-%d'


class AlpacaClient:
    """
    Wraps the Alpaca REST API: price bars, snapshots, news, and options open
    interest (used for PCR). Centralizes what used to be three separate
    REST(...) client constructions duplicated across stock_utils.
    """

    # Timeframes used for candlestick pattern detection (matches the labels
    # historically used by stock_routes.py's pattern endpoints).
    PATTERN_TIMEFRAMES = {
        '15Min': {'timeframe': TimeFrame(15, TimeFrameUnit.Minute), 'limit': 100},
        '30Min': {'timeframe': TimeFrame(30, TimeFrameUnit.Minute), 'limit': 50},
        '1Hour': {'timeframe': TimeFrame.Hour, 'limit': 750, 'start_key': 'one_month_ago'},
        '1Day': {'timeframe': TimeFrame.Day, 'limit': 367, 'start_key': 'year_ago'},
        '1Week': {'timeframe': TimeFrame.Week, 'limit': 264, 'start_key': 'five_year_ago'},
    }

    # Timeframes used by the price chart (matches chart_routes.py's labels).
    CHART_TIMEFRAMES = {
        '1D': {'timeframe': TimeFrame(1, TimeFrameUnit.Minute), 'limit': 1400},
        '1W': {'timeframe': TimeFrame.Hour, 'limit': 1400, 'start_key': 'one_week_ago', 'needs_end': True},
        '1M': {'timeframe': TimeFrame.Hour, 'limit': 1400, 'start_key': 'one_month_ago', 'needs_end': True},
        '3M': {'timeframe': TimeFrame.Day, 'limit': 1400, 'start_key': 'three_month_ago', 'needs_end': True},
        'YTD': {'timeframe': TimeFrame.Day, 'limit': 1400, 'start_key': 'start_of_year', 'needs_end': True},
        '1Y': {'timeframe': TimeFrame.Day, 'limit': 1400, 'start_key': 'year_ago', 'needs_end': True},
        '5Y': {'timeframe': TimeFrame.Week, 'limit': 1400, 'start_key': 'five_year_ago', 'needs_end': True},
    }

    def __init__(self, api_key=None, api_secret=None, base_url=None):
        self.api_key = api_key or os.getenv('API_KEY')
        self.api_secret = api_secret or os.getenv('API_SECRET')
        self.base_url = base_url or os.getenv('BASE_URL')
        self._rest = REST(base_url=self.base_url, key_id=self.api_key, secret_key=self.api_secret)

    @staticmethod
    def get_dates():
        today = datetime.now().date() - timedelta(days=1)
        return {
            'today': today.strftime(DATE_FORMAT),
            'one_week_ago': (today - timedelta(weeks=1)).strftime(DATE_FORMAT),
            'one_month_ago': (today - relativedelta(months=1)).strftime(DATE_FORMAT),
            'three_month_ago': (today - relativedelta(months=3)).strftime(DATE_FORMAT),
            'start_of_year': datetime(today.year, 1, 1).date().strftime(DATE_FORMAT),
            'year_ago': (today - relativedelta(years=1)).strftime(DATE_FORMAT),
            'five_year_ago': (today - relativedelta(years=5)).strftime(DATE_FORMAT),
        }

    def _get_bars(self, symbol, spec):
        dates = self.get_dates()
        kwargs = {'limit': spec['limit']}
        if 'start_key' in spec:
            kwargs['start'] = dates[spec['start_key']]
            if spec.get('needs_end'):
                kwargs['end'] = dates['today']
        return self._rest.get_bars(symbol, spec['timeframe'], **kwargs)

    def get_pattern_bars(self, symbol, timeframe_label):
        spec = self.PATTERN_TIMEFRAMES.get(timeframe_label, self.PATTERN_TIMEFRAMES['1Week'])
        return self._get_bars(symbol, spec)

    def get_chart_bars(self, symbol, timeframe_label):
        spec = self.CHART_TIMEFRAMES[timeframe_label]
        return self._get_bars(symbol, spec)

    def get_price(self, symbol):
        snapshot = self._rest.get_snapshot(symbol)
        return snapshot.minute_bar.vw

    def get_news(self, symbol, start, end):
        return self._rest.get_news(symbol, start=start, end=end, include_content=True)

    def get_put_call_open_interest(self, symbol, expiring_within_days=90):
        """
        Sums put/call open interest across active option contracts on
        `symbol` expiring within `expiring_within_days`. Returns (put_oi, call_oi).
        """
        cutoff = (datetime.now().date() + timedelta(days=expiring_within_days)).strftime(DATE_FORMAT)
        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret,
        }
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
            response = requests.get(f'{self.base_url}/v2/options/contracts', headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            for contract in data.get('option_contracts', []):
                oi = int(contract.get('open_interest') or 0)
                if contract.get('type') == 'put':
                    put_oi += oi
                elif contract.get('type') == 'call':
                    call_oi += oi
            page_token = data.get('next_page_token')
            if not page_token:
                break
        return put_oi, call_oi
