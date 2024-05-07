import "./StockNews.css";

function NewsTile({ news }) {
  const sentimentClassName =
    news.sentiment === "positive"
      ? "sentiment positive"
      : news.sentiment === "negative"
      ? "sentiment negative"
      : "sentiment neutral";
  console.log("we are here");
  return (
    <div className="stock-tile" style={{ position: "relative" }}>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          right: 0,
          padding: "2px 15px",
          fontSize: "14px",
          backgroundColor: "#89c0fb",
          border: "1px solid #dee2e6",
          borderRadius: "5px",
        }}
      >
        News
      </div>
      <h2 className="headline-author">
        {news.headline}
        <div>
          <div className="author"> By {news.author}</div>
          <div className="probabilty-sentiment">
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "center",
                gap: "10px",
              }}
            >
              <div className={sentimentClassName}>
                {news.sentiment.charAt(0).toUpperCase() +
                  news.sentiment.slice(1)}
              </div>
              <div>{(news.probability * 100).toFixed(2)}%</div>
            </div>
            <div style={{ fontSize: "13px" }}>
              {new Date(news.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </h2>
      <div className="stock-news-container">
        {news.images && news.images.length > 0 ? (
          <img
            src={news.images[0]["url"]}
            alt="news"
            style={{ width: "30%", height: "auto" }}
          />
        ) : null}
        <div>
          <p>{news.summary}</p>

          <p>Source: {news.source}</p>
          <p>Symbols: {news.symbols.join(", ")}</p>
        </div>
      </div>
      <a href={news.url} target="_blank" rel="noopener noreferrer">
        Read more
      </a>
    </div>
  );
}

export default NewsTile;
