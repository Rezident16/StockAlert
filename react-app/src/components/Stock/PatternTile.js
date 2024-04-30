import patternConversion from "./patternConversion";
import "./Pattern.css";
function PatternTile({pattern, currPrice, priceClass}) {
  const date = new Date(parseInt(pattern.milliseconds));
  const localDate = date.toLocaleDateString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
  const sentiment = pattern.sentiment;
  const stock = pattern.stock.symbol || "TEST";
  const timeframe = pattern.timeframe;
  const patternName = patternConversion(pattern.pattern_name);
  const sentimentClassName =
    sentiment === "Bullish" ? "positive pattern" : "negative pattern";
    const latestPrice = pattern.latest_price.toFixed(2)
    
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

      <div>
        <div>Price when caught: ${latestPrice}</div>
        <div style={{display: 'flex', flexDirection: 'row', alignItems: 'center'}}>Current Price: <p className={priceClass} style={{marginLeft: '3px'}}> ${currPrice}</p> <p style={{color: currPrice > latestPrice ? 'green' : 'red', fontWeight: 'bold', fontSize: '20px'}}>{currPrice > latestPrice ? '↑' : '↓'} ${(currPrice - latestPrice).toFixed(2)}</p></div>
      </div>
    </div>
  );
}

export default PatternTile;
