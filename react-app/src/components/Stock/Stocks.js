import react, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getStocksThunk } from "../../store/stocks";
import { useHistory } from "react-router-dom";

function StockList() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getStocksThunk());
  }, [dispatch]);

  const stocks = useSelector((state) => state.stocks.stocks);
  const [stockId, setStockId] = useState(null);
  const history = useHistory();
  if (!stocks) {
    return null;
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "200px",
        backgroundColor: "#4A154B",
      }}
    >
      {stocks.map((stock) => (
        <div
          key={stock.id}
          style={{ padding: "10px", borderBottom: "1px solid #3E0E40" }}
        >
          <p
            className="stock-name"
            onClick={() => history.push(`/stocks/${stock.id}`)}
            style={{ color: "#D3D3D3", cursor: "pointer" }}
          >
            {stock.symbol}
          </p>
        </div>
      ))}
    </div>
  );
}

export default StockList;
