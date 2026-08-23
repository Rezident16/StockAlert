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

    LONG_TREND_PERIOD = 200
    SHORT_TREND_PERIOD = 21
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 80
    RSI_LOWER_BOUND = 40
    RSI_UPPER_BOUND = 70

    def __init__(self, alpaca_client=None, pcr_signal=None):
        self.alpaca_client = alpaca_client or AlpacaClient()
        self.pcr_signal = pcr_signal or PCRSignal(alpaca_client=self.alpaca_client)

    def evaluate(self, symbol):
        closes = [bar.c for bar in self.alpaca_client.get_pattern_bars(symbol, '1Day')]

        if len(closes) < self.LONG_TREND_PERIOD:
            return {'signal': 'NEUTRAL', 'reasons': ['insufficient_price_history']}

        # Cast every indicator to a plain float here: numpy scalars compare
        # to numpy.bool_, not bool, and Flask's JSON encoder can't
        # serialize either numpy type.
        sma_long = float(TechnicalIndicators.sma(closes, self.LONG_TREND_PERIOD)[-1])
        ema_short = float(TechnicalIndicators.ema(closes, self.SHORT_TREND_PERIOD)[-1])
        rsi = float(TechnicalIndicators.rsi(closes, self.RSI_PERIOD)[-1])
        macd_line, macd_signal, _ = TechnicalIndicators.macd(closes)
        macd_line, macd_signal = float(macd_line[-1]), float(macd_signal[-1])

        price = float(closes[-1])
        pcr = self.pcr_signal.evaluate(symbol)

        above_long_trend = price > sma_long
        above_short_trend = price > ema_short
        macd_bullish = macd_line > macd_signal
        rsi_in_range = self.RSI_LOWER_BOUND <= rsi <= self.RSI_UPPER_BOUND
        pcr_bearish = pcr.get('signal') == 'SELL'
        pcr_bullish = pcr.get('signal') == 'BUY'

        buy_reasons = []
        if above_long_trend and above_short_trend and macd_bullish and rsi_in_range and not pcr_bearish:
            buy_reasons = ['price_above_sma200', 'price_above_ema21', 'macd_bullish', 'rsi_in_range']
            if pcr_bullish:
                buy_reasons.append('pcr_bullish')

        sell_reasons = []
        if not above_long_trend:
            sell_reasons.append('price_below_sma200')
        if rsi > self.RSI_OVERBOUGHT:
            sell_reasons.append('rsi_overbought')
        if macd_line < macd_signal:
            sell_reasons.append('macd_bearish')
        if pcr_bearish:
            sell_reasons.append('pcr_bearish')

        if buy_reasons:
            signal, reasons = 'BUY', buy_reasons
        elif sell_reasons:
            signal, reasons = 'SELL', sell_reasons
        else:
            signal, reasons = 'NEUTRAL', []

        return {
            'signal': signal,
            'reasons': reasons,
            'price': price,
            'sma200': sma_long,
            'ema21': ema_short,
            'rsi14': rsi,
            'macd_bullish': macd_bullish,
            'pcr': pcr,
        }
