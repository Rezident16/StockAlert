import React, { useEffect } from "react";
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
// import { getStockNewsThunk } from "../../store/stock";
import { getStockNewsThunk } from "../../store/news";
import { useSelector } from 'react-redux';
import NewsTile from "./NewsTile";

function StockNews() {
    const dispatch = useDispatch()
    const stock = useParams()
    useEffect(() => {
        dispatch(getStockNewsThunk(stock.id))
    }, [stock.id])

    const stockNews = useSelector(state => state.news.news).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    return (
        <div>
           {stockNews.map((news) => (
               <NewsTile key={news.id} news={news}/>
           ))}  
        </div>
    )
}

export default StockNews;
