import patternConversion from "./patternConversion";

function PatternTile({ pattern, currPrice, priceClass }) {
  const date = new Date(parseInt(pattern.milliseconds));
  const localDate = date.toLocaleDateString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
  const sentiment = pattern.sentiment;
  const stock = pattern.stock.symbol || "TEST";
  const timeframe = pattern.timeframe;
  const patternName = patternConversion(pattern.pattern_name);
  const isBullish = sentiment === "Bullish";
  const latestPrice = pattern.latest_price.toFixed(2);
  const priceUp = currPrice > latestPrice;

  const priceFlashClass =
    priceClass === "up-price"
      ? "bg-bullish/20"
      : priceClass === "down-price"
      ? "bg-bearish/20"
      : "bg-transparent";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm md:p-5">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-brand px-2.5 py-1 text-xs font-bold text-white">
            ${stock}
          </span>
          <span className="text-xs text-gray-400">{localDate}</span>
        </div>
        <span className="rounded-full border border-gray-200 bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
          Pattern
        </span>
      </div>

      <h3 className="mt-3 text-sm font-semibold text-gray-800">
        {patternName} <span className="text-gray-400">/ {timeframe}</span>
      </h3>

      <span
        className={
          "mt-2 inline-block rounded-full px-2.5 py-0.5 text-xs font-bold " +
          (isBullish
            ? "bg-bullish/15 text-bullish"
            : "bg-bearish/15 text-bearish")
        }
      >
        {sentiment}
      </span>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-600">
        <span>Caught at ${latestPrice}</span>
        <span className="flex items-center gap-1">
          Now
          <span className={`rounded px-1 transition-colors duration-500 ${priceFlashClass}`}>
            ${currPrice}
          </span>
        </span>
        <span
          className={`text-base font-bold ${priceUp ? "text-bullish" : "text-bearish"}`}
        >
          {priceUp ? "↑" : "↓"} ${Math.abs(currPrice - latestPrice).toFixed(2)}
        </span>
      </div>
    </div>
  );
}

export default PatternTile;
