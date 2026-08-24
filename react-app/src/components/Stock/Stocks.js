import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useHistory, useLocation } from "react-router-dom";
import { getStocksThunk } from "../../store/stocks";

function StockList() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getStocksThunk());
  }, [dispatch]);

  const stocks = useSelector((state) => state.stocks.stocks);
  const [search, setSearch] = useState("");
  const history = useHistory();
  const location = useLocation();
  if (!stocks) {
    return null;
  }

  const filteredStocks = stocks.filter((stock) =>
    stock.symbol.toLowerCase().includes(search.trim().toLowerCase())
  );

  return (
    <div className="flex w-full flex-col bg-brand lg:h-full lg:w-[220px] lg:shrink-0">
      <input
        type="text"
        placeholder="Search symbol..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="m-2.5 rounded border-none px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-white/40"
      />
      {filteredStocks.length === 0 ? (
        <p className="px-2.5 py-2 text-sm text-gray-300">No matches</p>
      ) : (
        <div className="flex gap-2 overflow-x-auto px-2.5 pb-2.5 lg:flex-col lg:gap-0 lg:overflow-visible lg:px-0 lg:pb-0">
          {filteredStocks.map((stock) => {
            const isActive = location.pathname.startsWith(`/stocks/${stock.id}`);
            return (
              <button
                key={stock.id}
                onClick={() => history.push(`/stocks/${stock.id}`)}
                className={
                  "shrink-0 whitespace-nowrap rounded-full px-3 py-1.5 text-sm font-semibold text-gray-200 transition-colors lg:rounded-none lg:border-b lg:border-brand-dark lg:px-4 lg:py-2.5 lg:text-left " +
                  (isActive
                    ? "bg-white/15 text-white lg:bg-white/10"
                    : "hover:bg-white/10")
                }
              >
                {stock.symbol}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default StockList;
