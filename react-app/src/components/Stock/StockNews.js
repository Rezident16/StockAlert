import React, { useEffect } from "react";
import { useParams } from "react-router-dom";
import { useDispatch } from "react-redux";
// import { getStockNewsThunk } from "../../store/stock";
import { getStockNewsThunk } from "../../store/news";
import { useSelector } from "react-redux";
import NewsTile from "./NewsTile";
import io from "socket.io-client"; // Import Socket.IO client library
import { useState } from "react";

function StockNews() {
  const dispatch = useDispatch();
  const stock = useParams();
  const [socket, setSocket] = useState(null); // State to hold the socket instance
  useEffect(() => {
    const fetchNews = () => dispatch(getStockNewsThunk(stock.id));
    fetchNews();

    const intervalId = setInterval(fetchNews, 25 * 60 * 1000);

    const newSocket = io.connect("localhost:5000/news");
    setSocket(newSocket);
    newSocket.on("news", (newsData) => {
    });
    return () => {
      newSocket.close();
      clearInterval(intervalId);
    };
  }, [stock.id, dispatch]);

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
