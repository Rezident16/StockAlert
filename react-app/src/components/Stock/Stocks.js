import react, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getStocksThunk } from '../../store/stocks';
import { useHistory } from 'react-router-dom';

function StockList() {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getStocksThunk());
    }, [dispatch]);

    const stocks = useSelector((state) => state.stocks.stocks);
    const history = useHistory()
    if (!stocks) {
        return null;
    }

    return (
        <div>
            {stocks.map((stock) => (
                <div key={stock.id}>
                    <p className='stock-name'  onClick={() => (history.push(`/stock/${stock.id}/patterns`))}>{stock.symbol}</p>
                </div>
            ))}
        </div>
    )
}

export default StockList;
