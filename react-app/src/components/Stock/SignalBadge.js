import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getStockSignalThunk } from "../../store/signal";
import "./SignalBadge.css";

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

  const signalClassName =
    signal.signal === "BUY"
      ? "signal-badge buy"
      : signal.signal === "SELL"
      ? "signal-badge sell"
      : "signal-badge neutral";

  const reasons = (signal.reasons || []).map(
    (reason) => REASON_LABELS[reason] || reason
  );

  return (
    <div className={signalClassName} title={reasons.join(", ")}>
      {signal.signal}
    </div>
  );
}

export default SignalBadge;
