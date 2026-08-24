import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import { getStockPriceThunk } from "../../store/stockPrice";
import { getStockPatternsThunk } from "../../store/patterns";
import { getStockNewsThunk } from "../../store/news";
import PatternTile from "./PatternTile";
import NewsTile from "./News/NewsTile";
import io from "socket.io-client";
import StockList from "./Stocks";
import StockChart, { TIMEFRAMES } from "./StockChart/StockChart";
import { getStockThunk } from "../../store/stock";
import FinvizData from "./finvizData";
import SignalBadge from "./SignalBadge";
import { API_BASE_URL } from "../../config";

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
    const socket = io(`${API_BASE_URL}/${endpoint}`);
    socket.on(event, (newItem) => {
      // newItem.stock_id is a number from the backend; id is always a
      // string (useParams()) - strict equality never matched.
      if (String(newItem.stock_id) === id) {
        setItem((prevItems) => [...prevItems, newItem]);
      }
    });
    return () => socket.disconnect();
  }, [id, setItem, endpoint, event]);
};

const usePriceEffect = (price, currPrice, setPriceClass) => {
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
  const [selectedOption, setSelectedOption] = useState("All");
  const [chartTimeframe, setChartTimeframe] = useState(5);
  const signalTimeframe =
    TIMEFRAMES.find((tf) => tf.id === chartTimeframe)?.label || "1Y";

  useFetchData(id, getStockNewsThunk);
  useFetchData(id, getStockPatternsThunk);
  useFetchData(id, getStockPriceThunk);
  useSocket(id, setPatterns, "patterns", "patterns");
  useSocket(id, setNews, "news", "news");
  usePriceEffect(price, currPrice, setPriceClass);

  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getStockThunk(id));
    setPatterns(currPatterns);
    setNews(currNews);
    setTimeout(() => setPrice(currPrice), 3000);
  }, [currPatterns, currNews, currPrice, id]);

  if (!patterns) return null;

  const handleSelectChange = (event) => {
    setSelectedOption(event.target.value);
  };

  const newsAndStocks = [...news, ...patterns].sort((a, b) => {
    const aTime = a.created_at
      ? new Date(a.created_at).getTime()
      : a.milliseconds;
    const bTime = b.created_at
      ? new Date(b.created_at).getTime()
      : b.milliseconds;
    return bTime - aTime;
  });

  return (
    <div className="flex flex-col lg:h-[calc(100vh-73px)] lg:flex-row">
      <div className="lg:h-full lg:overflow-y-auto">
        <StockList />
      </div>
      <div className="flex-1 overflow-y-auto px-3 py-4 md:px-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-3 md:gap-4">
          <SignalBadge id={id} timeframe={signalTimeframe} />
          <StockChart id={id} timeframe={chartTimeframe} setTimeframe={setChartTimeframe} />
          <FinvizData id={id} />
          <select
            className="ml-auto w-48 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm"
            value={selectedOption}
            onChange={handleSelectChange}
          >
            <option>All</option>
            <option>Patterns</option>
            <option>News</option>
          </select>

          {newsAndStocks.map((newsOrPattern) => {
            if (
              newsOrPattern.pattern_name &&
              (selectedOption === "Patterns" || selectedOption === "All")
            ) {
              return (
                <PatternTile
                  key={`pattern-${newsOrPattern.id}`}
                  pattern={newsOrPattern}
                  currPrice={currPrice}
                />
              );
            } else if (
              newsOrPattern.headline &&
              (selectedOption === "News" || selectedOption === "All")
            ) {
              return <NewsTile key={`news-${newsOrPattern.id}`} news={newsOrPattern} />;
            }
            return null;
          })}
        </div>
      </div>
    </div>
  );
}

export default NewsPatterns;
