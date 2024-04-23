import React, { useEffect } from "react";
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { getStockNewsThunk } from "../../store/stock";
import { useSelector } from 'react-redux';

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
            <h1>{stock.id}</h1>
        </div>
    )
}

export default StockNews;
