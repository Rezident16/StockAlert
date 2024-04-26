import React, { useEffect } from "react";
import { useParams } from "react-router-dom/cjs/react-router-dom.min";
import { useDispatch, useSelector } from "react-redux";
// import { getStockNewsThunk } from "../../store/news";
import { getStockPatternsThunk } from "../../store/patterns";
import PatternTile from "./PatternTile";

function StockPatterns() {
    const stock = useParams();
    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(getStockPatternsThunk(stock.id));
    }, [stock.id])
    const patterns = useSelector(state => state.patterns.patterns);
    let patternsArr = []
    for (let timeframe of patterns) {
        // console.log(Object.keys(timeframe))
        const keys = Object.keys(timeframe)
        for (let key of keys) {
            patternsArr.push(timeframe[key])
        }
    }
    patternsArr = patternsArr.flat()
    patternsArr = patternsArr.sort((a, b) => new Date(b.milliseconds) - new Date(a.milliseconds))
    console.log(patternsArr)
    return (
        <div>
            {patternsArr.map((pattern) => (
                <PatternTile pattern={pattern}/>
            ))}
        </div>
    )
}

export default StockPatterns;
