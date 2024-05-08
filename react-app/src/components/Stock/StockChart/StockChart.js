import React, { useState, useEffect } from "react";
import { fetchBars } from "./FetchBars";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import './Chart.css'

function StockChart({ id }) {
  const [barset, setBarset] = useState([]);
  const [timeframe, setTimeframe] = useState(0);

  useEffect(() => {
    const fetchAndSetBars = () =>
      fetchBars({ setBarset, stockId: id, timeframeId: timeframe });
    fetchAndSetBars();
    const interval = setInterval(fetchAndSetBars, 60000);
    return () => clearInterval(interval);
  }, [id, timeframe]);

  if (barset.length === 0) return <div>Loading...</div>;

  return (
    <div style={{
      marginTop: '10px',
    }}>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={barset}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" hide={true} />
          <YAxis domain={["dataMin", "dataMax"]} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#8884d8"
            dot={false}
            activeDot={false}
          />
          <Line
            type="monotone"
            dataKey="open"
            stroke="#82ca9d"
            dot={false}
            activeDot={false}
          />
          <ReferenceLine y={0} stroke="#000" />
        </LineChart>
      </ResponsiveContainer>
      <div
        className="timeframe-buttons"
      >
        <button
          className={timeframe === 0 ? "active-timeframe-button" : 'inactive-timeframe-button'}
          onClick={() => setTimeframe(0)}
        >
          1D
        </button>
        <button
          className={timeframe === 1 ? "active-timeframe-button" : 'inactive-timeframe-button'}
          onClick={() => setTimeframe(1)}
        >
          1W
        </button>
        <button
          className={timeframe === 2 ? "active-timeframe-button" : 'inactive-timeframe-button'}
          onClick={() => setTimeframe(2)}
        >
          1M
        </button>
        <button
          className={timeframe === 3 ? "active-timeframe-button" : 'inactive-timeframe-button'}
          onClick={() => setTimeframe(3)}
        >
          3M
        </button>
        <button
          className={timeframe === 6 ? "active-timeframe-button" : 'inactive-timeframe-button'}
          onClick={() => setTimeframe(6)}
        >
          YTD
        </button>
        <button
          className={timeframe === 4 ? "active-timeframe-button" : 'inactive-timeframe-button'}
          onClick={() => setTimeframe(4)}
        >
          1Y
        </button>
        <button
          className={timeframe === 5 ? "active-timeframe-button" : 'inactive-timeframe-button'}
          onClick={() => setTimeframe(5)}
        >
          5Y
        </button>
      </div>
    </div>
  );
}

export default StockChart;
