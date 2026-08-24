import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getStockSignalThunk } from "../../store/signal";

const SIGNAL_STYLES = {
  BUY: "bg-bullish/15 text-bullish border-bullish/40",
  SELL: "bg-bearish/15 text-bearish border-bearish/40",
  NEUTRAL: "bg-gray-100 text-gray-500 border-gray-300",
};

function SignalBadge({ id, timeframe }) {
  const dispatch = useDispatch();
  const signal = useSelector((state) => state.signal.signal);

  useEffect(() => {
    dispatch(getStockSignalThunk(id, timeframe));
    const intervalId = setInterval(() => {
      dispatch(getStockSignalThunk(id, timeframe));
    }, 60000);
    return () => clearInterval(intervalId);
  }, [dispatch, id, timeframe]);

  if (!signal) return null;

  const reasons = signal.reasons || [];

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border border-gray-200 bg-white p-3 shadow-sm md:p-4">
      <span
        className={`rounded-full border px-4 py-1.5 text-sm font-extrabold tracking-wide ${SIGNAL_STYLES[signal.signal] || SIGNAL_STYLES.NEUTRAL}`}
      >
        {signal.signal}
      </span>
      {reasons.map((reason) => (
        <span
          key={reason}
          className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600"
        >
          {reason}
        </span>
      ))}
    </div>
  );
}

export default SignalBadge;
