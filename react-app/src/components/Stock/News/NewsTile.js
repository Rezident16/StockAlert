function NewsTile({ news }) {
  const isPositive = news.sentiment === "Positive";
  const isNegative = news.sentiment === "Negative";
  const sentimentClass = isPositive
    ? "bg-bullish/15 text-bullish"
    : isNegative
    ? "bg-bearish/15 text-bearish"
    : "bg-gray-200 text-gray-600";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm md:p-5">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          {news.symbols &&
            news.symbols.map((symbol) => (
              <span
                key={symbol}
                className="rounded-full bg-brand px-2.5 py-1 text-xs font-bold text-white"
              >
                ${symbol}
              </span>
            ))}
        </div>
        <span className="shrink-0 rounded-full border border-gray-200 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
          News
        </span>
      </div>

      <h2 className="mt-3 text-base font-semibold text-gray-800">
        {news.headline}
      </h2>
      <div className="mt-1 text-sm text-gray-500">By {news.author}</div>

      <div className="mt-2 flex flex-wrap items-center gap-3">
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${sentimentClass}`}>
          {news.sentiment.charAt(0).toUpperCase() + news.sentiment.slice(1)}
        </span>
        <span className="text-xs text-gray-500">
          {(news.probability * 100).toFixed(2)}% confidence
        </span>
        <span className="text-xs text-gray-400">
          {new Date(news.created_at).toLocaleString()}
        </span>
      </div>

      <div className="mt-3 flex flex-col gap-3 sm:flex-row">
        {news.images && news.images.length > 0 ? (
          <img
            src={news.images[0]["url"]}
            alt={news.headline}
            className="w-full rounded-lg object-cover sm:w-1/3"
          />
        ) : null}
        <div className="flex-1 text-sm text-gray-700">
          <p>{news.summary}</p>
          <p className="mt-2 text-gray-500">Source: {news.source}</p>
        </div>
      </div>

      <a
        href={news.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-3 inline-block text-sm font-medium text-blue-600 hover:underline"
      >
        Read more
      </a>
    </div>
  );
}

export default NewsTile;
