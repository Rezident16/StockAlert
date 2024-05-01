import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom/cjs/react-router-dom.min";
import { useDispatch, useSelector } from "react-redux";
import { getStockPatternsThunk } from "../../store/patterns";
import PatternTile from "./PatternTile";
import { getStockPriceThunk } from "../../store/stockPrice";
import io from "socket.io-client";
import StockList from "./Stocks";

function StockPatterns() {
  const stock = useParams();
  const dispatch = useDispatch();
  const currPatterns = useSelector((state) => state.patterns.patterns);
  const [patterns, setPatterns] = useState([]);
  const currPrice = useSelector((state) => state.price.price);
  const [price, setPrice] = useState(currPrice);
  const [priceClass, setPriceClass] = useState("neutral-price");

  useEffect(() => {
    setPatterns(currPatterns);
  }, [currPatterns]);

  useEffect(() => {
    dispatch(getStockPatternsThunk(stock.id));
    const intervalId = setInterval(() => {
      console.log("fetching stock price");
      dispatch(getStockPriceThunk(stock.id));
    }, 5000);
    return () => clearInterval(intervalId);
  }, [dispatch, stock.id]);

  useEffect(() => {
    const socket = io("http://localhost:5000/patterns");

    socket.on("connect", () => {
      console.log("Connected to server");
    });

    socket.on("patterns", (newPattern) => {
      console.log("New stock pattern emitted:", newPattern);
      if (newPattern.stock_id === stock.id) {
        setPatterns((prevPatterns) => [...prevPatterns, newPattern]);
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [stock.id]);

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

  useEffect(() => {
    setTimeout(() => setPrice(currPrice), 3000);
  }, [currPrice]);

  if (!patterns) {
    return null;
  }

  const sortedPatterns = patterns.sort((a, b) => b.milliseconds - a.milliseconds);
  return (
    <div className="container">
      <div className="stock-list">
        <StockList />
      </div>
      <div className="patterns">
        {sortedPatterns.map((pattern, index) => (
          <div key={index}>
            <PatternTile
              pattern={pattern}
              currPrice={currPrice}
              priceClass={priceClass}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default StockPatterns;
