import React, { useEffect } from "react";
import { useParams } from "react-router-dom/cjs/react-router-dom.min";
import { useDispatch, useSelector } from "react-redux";
// import { getStockNewsThunk } from "../../store/news";
import { getStockPatternsThunk } from "../../store/patterns";
import PatternTile from "./PatternTile";
import getStockPrice from './stockPrice'
import { getStockPriceThunk } from "../../store/stockPrice";

function StockPatterns() {
  const stock = useParams();
  const dispatch = useDispatch();
  
//   const getStockPrice = require('./stockPrice')
//   getStockPrice()

useEffect(() => {
    dispatch(getStockPatternsThunk(stock.id));
    dispatch(getStockPriceThunk(stock.id));
}, [stock.id]);
let patterns = useSelector((state) => state.patterns.patterns);
let currPrice = useSelector((state) => state.price.price);
if (!patterns) {
  return null;
}
  patterns = patterns.sort(
    (a, b) => b.milliseconds - a.milliseconds
  );
  return (
    <div>
      {patterns.map((pattern) => (
        <PatternTile pattern={pattern} currPrice = {currPrice}/>
      ))}
    </div>
  );
}

export default StockPatterns;
