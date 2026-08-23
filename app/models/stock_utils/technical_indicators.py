import numpy as np
import pandas as pd


class TechnicalIndicators:
    """
    Stateless technical-indicator math shared by the signal classes. Ported
    from the leveraged-ETF bot's hand-rolled indicator primitives
    (~/Desktop/TradingBotActions/LeveragedETFBot/lev_etf_bot.py) - only the
    pure math, none of its trading/execution/ML logic.
    """

    @staticmethod
    def sma(closes, n):
        return pd.Series(closes, dtype=float).rolling(n).mean().to_numpy()

    @staticmethod
    def ema(closes, n):
        return pd.Series(closes, dtype=float).ewm(span=n, adjust=False).mean().to_numpy()

    @staticmethod
    def realized_volatility(closes, n=21):
        """Annualized realized volatility: std(log returns, n) * sqrt(252)."""
        closes = np.asarray(closes, dtype=float)
        log_returns = np.diff(np.log(closes))
        rolling_std = pd.Series(log_returns).rolling(n).std().to_numpy()
        return np.concatenate([[np.nan], rolling_std * np.sqrt(252)])

    @staticmethod
    def rate_of_change(closes, n):
        closes = np.asarray(closes, dtype=float)
        roc = np.full(len(closes), np.nan)
        if len(closes) > n:
            roc[n:] = closes[n:] / closes[:-n] - 1.0
        return roc

    @staticmethod
    def rolling_max(values, n):
        return pd.Series(values, dtype=float).rolling(n).max().to_numpy()

    @staticmethod
    def macd(closes, fast=12, slow=26, signal=9):
        """Returns (macd_line, signal_line, histogram)."""
        macd_line = TechnicalIndicators.ema(closes, fast) - TechnicalIndicators.ema(closes, slow)
        signal_line = pd.Series(macd_line).ewm(span=signal, adjust=False).mean().to_numpy()
        return macd_line, signal_line, macd_line - signal_line

    @staticmethod
    def rsi(closes, n=14):
        """Wilder's RSI."""
        delta = pd.Series(closes, dtype=float).diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()
        rs = avg_gain / avg_loss
        return (100 - (100 / (1 + rs))).to_numpy()

    @staticmethod
    def atr(highs, lows, closes, n=14):
        """True range, SMA-smoothed."""
        highs, lows, closes = pd.Series(highs, dtype=float), pd.Series(lows, dtype=float), pd.Series(closes, dtype=float)
        prev_close = closes.shift(1)
        true_range = pd.concat([
            highs - lows,
            (highs - prev_close).abs(),
            (lows - prev_close).abs(),
        ], axis=1).max(axis=1)
        return true_range.rolling(n).mean().to_numpy()

    @staticmethod
    def adx(highs, lows, closes, n=14):
        """Wilder's ADX."""
        highs, lows, closes = pd.Series(highs, dtype=float), pd.Series(lows, dtype=float), pd.Series(closes, dtype=float)
        up_move = highs.diff()
        down_move = -lows.diff()
        plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0))
        minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0))

        prev_close = closes.shift(1)
        true_range = pd.concat([
            highs - lows,
            (highs - prev_close).abs(),
            (lows - prev_close).abs(),
        ], axis=1).max(axis=1)

        smoothed_tr = true_range.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()
        plus_di = 100 * plus_dm.ewm(alpha=1 / n, min_periods=n, adjust=False).mean() / smoothed_tr
        minus_di = 100 * minus_dm.ewm(alpha=1 / n, min_periods=n, adjust=False).mean() / smoothed_tr
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        return dx.ewm(alpha=1 / n, min_periods=n, adjust=False).mean().to_numpy()

    @staticmethod
    def mfi(highs, lows, closes, volumes, n=14):
        """Money Flow Index. Requires per-bar volume data."""
        highs, lows, closes, volumes = (pd.Series(highs, dtype=float), pd.Series(lows, dtype=float),
                                         pd.Series(closes, dtype=float), pd.Series(volumes, dtype=float))
        typical_price = (highs + lows + closes) / 3
        raw_money_flow = typical_price * volumes
        direction = typical_price.diff()

        positive_flow = raw_money_flow.where(direction > 0, 0.0).rolling(n).sum()
        negative_flow = raw_money_flow.where(direction < 0, 0.0).rolling(n).sum()

        money_ratio = positive_flow / negative_flow
        return (100 - (100 / (1 + money_ratio))).to_numpy()

    @staticmethod
    def trix(closes, n=15):
        """1-period rate of change of a triple-smoothed EMA."""
        ema1 = TechnicalIndicators.ema(closes, n)
        ema2 = TechnicalIndicators.ema(ema1, n)
        ema3 = TechnicalIndicators.ema(ema2, n)
        return (pd.Series(ema3).pct_change() * 100).to_numpy()
