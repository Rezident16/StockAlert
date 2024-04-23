import "./StockNews.css";

function StockTile({ news }) {
  return (
    <div className="stock-tile">
      <h2>{news.headline}</h2>
        <h3>By {news.author}</h3>
      <div className="stock-news-container">
        {news.images && news.images.length > 0 ? (
          <img
            src={news.images[0]["url"]}
            alt="news"
            style={{ width: "30%", height: "auto" }}
          />
        ) : null}
        <div>
        <p>{news.created_at}</p>
        <p>{news.summary}</p>
        <p>Sentiment: {news.sentiment}</p>
        <p>Probability: {news.probability}</p>
        <p>Source: {news.source}</p>
        <p>Symbols: {news.symbols.join(", ")}</p>
        </div>
      </div>
      <a href={news.url} target="_blank" rel="noopener noreferrer">Read more</a>
    </div>
  );
}

export default StockTile;
