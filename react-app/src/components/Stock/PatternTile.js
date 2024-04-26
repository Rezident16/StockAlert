import patternConversion from "./patternConversion";
import "./Pattern.css";

function PatternTile(pattern) {
  pattern = pattern.pattern;

  const date = new Date(pattern.milliseconds);
  const localDate = date.toLocaleDateString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
  const sentiment = pattern.sentiment;
  const stock = pattern.stock;
  const timeframe = pattern.timeframe;
  const patternName = patternConversion(pattern.pattern);
  const sentimentClassName = sentiment === "Bullish" ? "positive pattern" : "negative pattern";
  /*
    date
    milliseconds
    pattern
    sentiment
    stock
    timeframe
    value
    */
  return (
    <div className="pattern-container">
      <div className="stock-date">
        <h2>{stock}</h2>
        <div>{localDate}</div>
      </div>

      <h3 className="pattern-time">
        {patternName} / {timeframe}
      </h3>
      <div className={sentimentClassName}> {sentiment}</div>
    </div>
  );
}

export default PatternTile;
