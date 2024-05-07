import patternConversion from "./patternConversion";
import "./Pattern.css";
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
  const sentimentClassName =
    sentiment === "Bullish" ? "positive pattern" : "negative pattern";
  const latestPrice = pattern.latest_price.toFixed(2);

  return (
    <div className="pattern-container" style={{ position: "relative" }}>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          right: 0,
          padding: "2px 15px",
          fontSize: "14px",
          backgroundColor: "#f9d51282",
          border: "1px solid #dee2e6",
          borderRadius: "5px",
        }}
      >
        Pattern
      </div>
      <div className="stock-date">
        <h2 style={{ margin: "0", color: "#2C2D30" }}>{stock}</h2>
        <div style={{ color: "black" }}>{localDate}</div>
      </div>

      <h3 className="pattern-time">
        {patternName} / {timeframe}
      </h3>
      <div
        className={sentimentClassName}
        style={{
          color: sentiment === "Bullish" ? "green" : "red",
          fontWeight: "bold",
          marginBottom: "10px",
        }}
      >
        {" "}
        {sentiment}
      </div>

      <div>
        <div style={{ color: "black" }}>Price when caught: ${latestPrice}</div>
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            color: "black",
          }}
        >
          Current Price:{" "}
          <p className={priceClass} style={{ marginLeft: "3px" }}>
            {" "}
            ${currPrice}
          </p>{" "}
          <p
            style={{
              color: currPrice > latestPrice ? "green" : "red",
              fontWeight: "bold",
              fontSize: "20px",
            }}
          >
            {currPrice > latestPrice ? "↑" : "↓"} $
            {(currPrice - latestPrice).toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
}

export default PatternTile;
