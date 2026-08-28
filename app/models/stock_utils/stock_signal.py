from .alpaca_client import AlpacaClient
from .pcr_signal import PCRSignal
from .technical_indicators import TechnicalIndicators


class StockSignal:
    """
    Generic BUY/SELL/NEUTRAL signal for any stock, built from the same kind
    of trend/momentum/PCR building blocks the leveraged-ETF bot's per-ETF
    strategies use (~/Desktop/TradingBotActions/LeveragedETFBot/lev_etf_bot.py:
    price vs SMA200/EMA21, RSI, MACD, PCR), generalized to run on a single
    stock's own price series instead of a fixed set of hardcoded ETFs and
    their companion tickers (QQQ/SMH/VGT/XLF/ITB/HYG).

    Read-only: there's no tracked position or entry price here (this app
    doesn't place trades), so this reports trend regime/momentum breakdown,
    not the original bot's stop-loss-based "you're down 15%, exit" logic -
    that specific exit condition doesn't generalize to a symbol nobody is
    known to hold.
    """

    # Moving-average lengths scale with the selected chart timeframe - a
    # 200-day SMA doesn't mean much to someone looking at a 1-day chart.
    # Bars stay daily-granularity regardless (reliable up to ~367 bars via
    # AlpacaClient.PATTERN_TIMEFRAMES['1Day']; the shorter Alpaca
    # granularities used for candlestick patterns - 15Min/30Min - don't
    # fetch enough bars to support even the shortest of these windows).
    TIMEFRAME_PERIODS = {
        '1D': {'long': 10, 'short': 5},
        '1W': {'long': 20, 'short': 9},
        '1M': {'long': 50, 'short': 13},
        '3M': {'long': 90, 'short': 21},
        'YTD': {'long': 200, 'short': 21},
        '1Y': {'long': 200, 'short': 21},
        '5Y': {'long': 200, 'short': 50},
    }
    DEFAULT_TIMEFRAME = '1Y'

    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 80
    RSI_LOWER_BOUND = 40
    RSI_UPPER_BOUND = 70

    REASON_LABELS = {
        'price_above_long_ma': 'Price above its longer-term moving average',
        'price_above_short_ma': 'Price above its shorter-term moving average',
        'price_below_long_ma': 'Price below its longer-term moving average',
        'macd_bullish': 'MACD bullish',
        'macd_bearish': 'MACD bearish',
        'rsi_in_range': 'RSI in a healthy range',
        'rsi_overbought': 'RSI overbought',
        'pcr_bullish': 'Put/call ratio bullish',
        'pcr_bearish': 'Put/call ratio bearish',
        'insufficient_price_history': 'Not enough price history yet',
    }

    def __init__(self, alpaca_client=None, pcr_signal=None):
        self.alpaca_client = alpaca_client or AlpacaClient()
        self.pcr_signal = pcr_signal or PCRSignal(alpaca_client=self.alpaca_client)

    def evaluate(self, symbol, timeframe=DEFAULT_TIMEFRAME):
        periods = self.TIMEFRAME_PERIODS.get(timeframe, self.TIMEFRAME_PERIODS[self.DEFAULT_TIMEFRAME])
        long_period, short_period = periods['long'], periods['short']

        closes = [bar.c for bar in self.alpaca_client.get_pattern_bars(symbol, '1Day')]

        if len(closes) < long_period:
            return self._result('NEUTRAL', ['insufficient_price_history'])

        # Cast every indicator to a plain float here: numpy scalars compare
        # to numpy.bool_, not bool, and Flask's JSON encoder can't
        # serialize either numpy type.
        long_ma = float(TechnicalIndicators.sma(closes, long_period)[-1])
        short_ma = float(TechnicalIndicators.ema(closes, short_period)[-1])
        rsi = float(TechnicalIndicators.rsi(closes, self.RSI_PERIOD)[-1])
        macd_line, macd_signal, _ = TechnicalIndicators.macd(closes)
        macd_line, macd_signal = float(macd_line[-1]), float(macd_signal[-1])

        price = float(closes[-1])
        pcr = self.pcr_signal.evaluate(symbol)

        above_long_trend = price > long_ma
        above_short_trend = price > short_ma
        macd_bullish = macd_line > macd_signal
        rsi_in_range = self.RSI_LOWER_BOUND <= rsi <= self.RSI_UPPER_BOUND
        pcr_bearish = pcr.get('signal') == 'SELL'
        pcr_bullish = pcr.get('signal') == 'BUY'

        # Every flag that actually fired, both bullish and bearish - not
        # just whichever side ends up deciding the overall call. A stock
        # can be a technical BUY while still flashing an RSI-overbought
        # warning, and that warning shouldn't disappear just because the
        # buy conditions also happened to be met.
        bullish_flags = []
        if above_long_trend:
            bullish_flags.append('price_above_long_ma')
        if above_short_trend:
            bullish_flags.append('price_above_short_ma')
        if macd_bullish:
            bullish_flags.append('macd_bullish')
        if rsi_in_range:
            bullish_flags.append('rsi_in_range')
        if pcr_bullish:
            bullish_flags.append('pcr_bullish')

        bearish_flags = []
        if not above_long_trend:
            bearish_flags.append('price_below_long_ma')
        if rsi > self.RSI_OVERBOUGHT:
            bearish_flags.append('rsi_overbought')
        if not macd_bullish:
            bearish_flags.append('macd_bearish')
        if pcr_bearish:
            bearish_flags.append('pcr_bearish')

        buy_conditions_met = above_long_trend and above_short_trend and macd_bullish and rsi_in_range and not pcr_bearish
        sell_conditions_met = bool(bearish_flags)

        if buy_conditions_met:
            signal = 'BUY'
        elif sell_conditions_met:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'

        # De-dupe while preserving order (a flag can't appear in both lists).
        reasons = bullish_flags + bearish_flags

        indicators = self._build_indicators(
            price=price, long_ma=long_ma, short_ma=short_ma, long_period=long_period,
            short_period=short_period, above_long_trend=above_long_trend,
            above_short_trend=above_short_trend, rsi=rsi, macd_line=macd_line,
            macd_signal=macd_signal, macd_bullish=macd_bullish, pcr=pcr,
        )

        return self._result(signal, reasons, indicators=indicators, price=price, long_ma=long_ma,
                             short_ma=short_ma, long_period=long_period, short_period=short_period,
                             rsi=rsi, macd_bullish=macd_bullish, pcr=pcr, timeframe=timeframe)

    def _build_indicators(self, price, long_ma, short_ma, long_period, short_period,
                           above_long_trend, above_short_trend, rsi, macd_line, macd_signal,
                           macd_bullish, pcr):
        """
        A per-indicator good/bad/neutral breakdown for display (e.g. a
        table), independent of `reasons` above - every indicator gets a
        row here regardless of which side it fell on, rather than only the
        ones that happened to fire a flag.
        """
        indicators = [
            {
                'name': f'Price vs {long_period}-day trend',
                'value': f'${price:.2f} vs ${long_ma:.2f}',
                'status': 'good' if above_long_trend else 'bad',
            },
            {
                'name': f'Price vs {short_period}-day trend',
                'value': f'${price:.2f} vs ${short_ma:.2f}',
                'status': 'good' if above_short_trend else 'bad',
            },
            {
                'name': f'RSI ({self.RSI_PERIOD})',
                'value': f'{rsi:.1f}',
                'status': self._rsi_status(rsi),
            },
            {
                'name': 'MACD',
                'value': f'{macd_line:.2f} vs {macd_signal:.2f}',
                'status': 'good' if macd_bullish else 'bad',
            },
        ]
        if pcr.get('available'):
            indicators.append({
                'name': 'Put/call ratio',
                'value': f'{pcr["pcr"]:.2f}',
                'status': self._pcr_status(pcr['sentiment']),
            })
        return indicators

    def _rsi_status(self, rsi):
        if rsi > self.RSI_OVERBOUGHT:
            return 'bad'
        if self.RSI_LOWER_BOUND <= rsi <= self.RSI_UPPER_BOUND:
            return 'good'
        return 'neutral'

    @staticmethod
    def _pcr_status(sentiment):
        if sentiment in ('fear_contrarian_bullish', 'slightly_bullish'):
            return 'good'
        if sentiment == 'complacency_contrarian_bearish':
            return 'bad'
        return 'neutral'

    def _result(self, signal, reason_codes, indicators=None, **extra):
        return {
            'signal': signal,
            'reasons': [self.REASON_LABELS.get(code, code) for code in reason_codes],
            'indicators': indicators or [],
            **extra,
        }
