import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getStocksThunk } from "../../store/stocks";
import { useHistory } from "react-router-dom";

function StockList() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getStocksThunk());
  }, [dispatch]);

  const stocks = useSelector((state) => state.stocks.stocks);
  const [search, setSearch] = useState("");
  const history = useHistory();
  if (!stocks) {
    return null;
  }

  const filteredStocks = stocks.filter((stock) =>
    stock.symbol.toLowerCase().includes(search.trim().toLowerCase())
  );

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "200px",
        backgroundColor: "#4A154B",
      }}
    >
      <input
        type="text"
        placeholder="Search symbol..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{
          margin: "10px",
          padding: "6px 8px",
          borderRadius: "4px",
          border: "none",
        }}
      />
      {filteredStocks.length === 0 ? (
        <p style={{ color: "#D3D3D3", padding: "10px" }}>No matches</p>
      ) : (
        filteredStocks.map((stock) => (
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
        ))
      )}
    </div>
  );
}

export default StockList;
