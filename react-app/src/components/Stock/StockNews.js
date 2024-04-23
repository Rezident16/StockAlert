import React, { useEffect } from "react";
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { getStockNewsThunk } from "../../store/stock";
import { useSelector } from 'react-redux';
import StockTile from "./StockTile";

function StockNews() {
    const dispatch = useDispatch()
    const stock = useParams()
    useEffect(() => {
        dispatch(getStockNewsThunk(stock.id))
    }, [stock.id, dispatch])

    const stockNews = useSelector(state => state.stock.news)
    console.log(stockNews)
    return (
        <div>
           {stockNews.map((news) => (
               <StockTile key={news.id} news={news}/>
           ))}  
        </div>
    )
}

export default StockNews;
