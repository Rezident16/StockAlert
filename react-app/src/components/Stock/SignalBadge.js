import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getStockSignalThunk } from "../../store/signal";

const REASON_LABELS = {
  price_above_sma200: "Price above 200-day average",
  price_above_ema21: "Price above 21-day average",
  macd_bullish: "MACD bullish",
  macd_bearish: "MACD bearish",
  rsi_in_range: "RSI in healthy range",
  rsi_overbought: "RSI overbought",
  price_below_sma200: "Price below 200-day average",
  pcr_bullish: "Put/call ratio bullish",
  pcr_bearish: "Put/call ratio bearish",
  insufficient_price_history: "Not enough price history yet",
};

const SIGNAL_STYLES = {
  BUY: "bg-bullish/15 text-bullish border-bullish/40",
  SELL: "bg-bearish/15 text-bearish border-bearish/40",
  NEUTRAL: "bg-gray-100 text-gray-500 border-gray-300",
};

function SignalBadge({ id }) {
  const dispatch = useDispatch();
  const signal = useSelector((state) => state.signal.signal);

  useEffect(() => {
    dispatch(getStockSignalThunk(id));
    const intervalId = setInterval(() => {
      dispatch(getStockSignalThunk(id));
    }, 60000);
    return () => clearInterval(intervalId);
  }, [dispatch, id]);

  if (!signal) return null;

  const reasons = (signal.reasons || []).map(
    (reason) => REASON_LABELS[reason] || reason
  );

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border border-gray-200 bg-white p-3 shadow-sm md:p-4">
      <span
        title={reasons.join(", ")}
        className={`rounded-full border px-4 py-1.5 text-sm font-extrabold tracking-wide ${SIGNAL_STYLES[signal.signal] || SIGNAL_STYLES.NEUTRAL}`}
      >
        {signal.signal}
      </span>
      {reasons.length > 0 && (
        <span className="text-xs text-gray-500">{reasons.join(" · ")}</span>
      )}
    </div>
  );
}

export default SignalBadge;
