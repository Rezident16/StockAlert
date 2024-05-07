import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import { getStockPriceThunk } from "../../store/stockPrice";
import { getStockPatternsThunk } from "../../store/patterns";
import { getStockNewsThunk } from "../../store/news";
import PatternTile from "./PatternTile";
import NewsTile from "./NewsTile";
import io from "socket.io-client";
import StockList from "./Stocks";
import StockChart from "./StockChart/StockChart";

const useFetchData = (id, thunk, interval = 5000) => {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(thunk(id));
    const intervalId = setInterval(() => {
      dispatch(thunk(id));
    }, interval);
    return () => clearInterval(intervalId);
  }, [id, dispatch, thunk, interval]);
};

const useSocket = (id, setItem, endpoint, event) => {
  useEffect(() => {
    const socket = io(`http://localhost:5000/${endpoint}`);
    socket.on(event, (newItem) => {
      if (newItem.stock_id === id) {
        setItem((prevItems) => [...prevItems, newItem]);
      }
    });
    return () => socket.disconnect();
  }, [id, setItem, endpoint, event]);
};

function NewsPatterns() {
  const id = useParams().id;
  const currNews = useSelector((state) => state.news.news);
  const currPrice = useSelector((state) => state.price.price);
  const currPatterns = useSelector((state) => state.patterns.patterns);
  const [patterns, setPatterns] = useState([]);
  const [news, setNews] = useState([]);
  const [price, setPrice] = useState(currPrice);
  const [priceClass, setPriceClass] = useState("neutral-price");

  useFetchData(id, getStockNewsThunk);
  useFetchData(id, getStockPatternsThunk);
  useFetchData(id, getStockPriceThunk);
  useSocket(id, setPatterns, "patterns", "patterns");
  useSocket(id, setNews, "news", "news");

  useEffect(() => {
    setPatterns(currPatterns);
    setNews(currNews);
  }, [currPatterns, currNews]);

  let newsAndStocks = [...news, ...patterns];
  newsAndStocks.sort((a, b) => {
    const aTime = a.created_at
      ? new Date(a.created_at).getTime()
      : a.milliseconds;
    const bTime = b.created_at
      ? new Date(b.created_at).getTime()
      : b.milliseconds;
    return bTime - aTime;
  });

  useEffect(() => {
    if (price > currPrice) {
      setPriceClass("down-price");
      setTimeout(() => setPriceClass("neutral-price"), 500);
    } else if (price < currPrice) {
      setPriceClass("up-price");
      setTimeout(() => setPriceClass("neutral-price"), 500);
    } else {
      setPriceClass("neutral-price");
    }
  }, [price, currPrice]);

  useEffect(() => setTimeout(() => setPrice(currPrice), 3000), [currPrice]);

  if (!patterns) return null;

  return (
    <div className="container">
      <div className="stock-list">
        <StockList />
      </div>
      <div className="patterns">
        <StockChart id={id} />
        {newsAndStocks.map((newsOrPattern) => {
          if (newsOrPattern.pattern_name) {
            return (
              <PatternTile
                key={newsOrPattern.id}
                pattern={newsOrPattern}
                currPrice={currPrice}
              />
            );
          } else if (newsOrPattern.headline) {
            return <NewsTile key={newsOrPattern.id} news={newsOrPattern} />;
          }
        })}
      </div>
    </div>
  );
}

export default NewsPatterns;
