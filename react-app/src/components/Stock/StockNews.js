import React from "react";
import { useSelector } from "react-redux";
import NewsTile from "./News/NewsTile";

function StockNews() {
  const stockNews = useSelector((state) => state.news.news).sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
  return (
    <div>
      {stockNews.map((news) => (
        <NewsTile key={news.id} news={news} />
      ))}
    </div>
  );
}

export default StockNews;
