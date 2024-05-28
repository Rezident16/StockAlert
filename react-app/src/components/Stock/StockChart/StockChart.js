import React, { useState, useEffect } from "react";
import { fetchBars, fetchChartPatterns } from "./FetchBars";
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
import "./Chart.css";
import { useSelector } from "react-redux";

function StockChart({ id }) {
  const [barset, setBarset] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [timeframe, setTimeframe] = useState(5);

  useEffect(() => {
    const fetchAndSetBars = () =>
      fetchBars({ setBarset, stockId: id, timeframeId: timeframe });
    fetchChartPatterns({ setPatterns, stockId: id, timeframeId: timeframe });
    fetchAndSetBars();
    const interval = setInterval(fetchAndSetBars, 60000);
    return () => clearInterval(interval);
  }, [id, timeframe]);

  const stock = useSelector((state) => state.stock);
  console.log(stock.symbol)

  if (barset.length === 0) return <div>Loading...</div>;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const matchingPatterns = patterns.filter(
        (pattern) => pattern.date === label
      );
      return (
        <div className="custom-tooltip">
          <p className="label">{`Date : ${label}`}</p>
          <p className="intro open">{`Open : ${payload[1].value}`}</p>
          <p className="intro close">{`Close : ${payload[0].value}`}</p>
          <div className="tooltip-patterns">
            {matchingPatterns && matchingPatterns.length > 0 && (
              <h4 style={{ margin: "5px 0px" }}>Patterns:</h4>
            )}
            {matchingPatterns &&
              matchingPatterns.map((pattern) => {
                const sentimentClass =
                  pattern.sentiment === "Bullish"
                    ? "bullish desc"
                    : "bearish desc";
                return (
                  <p
                    className={sentimentClass}
                  >{`${pattern.pattern_name}/${pattern.timeframe} - ${pattern.sentiment}`}</p>
                );
              })}
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div
      style={{
        marginTop: "10px",
      }}
    >
      <ResponsiveContainer
        width="100%"
        height={300}
        style={{ overflow: "visible" }}
      >
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
          <Tooltip content={<CustomTooltip />} />
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
            // dot={false}
            activeDot={false}
            dot={(props) => {
              const { cx, cy, payload } = props;
              if (patterns.some((pattern) => pattern.date === payload.date)) {
                const pattern = patterns.find(
                  (pattern) => pattern.date === payload.date
                );
                return (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={4}
                    stroke="orange"
                    strokeWidth={2}
                    fill="white"
                    title={`Pattern Name: ${pattern.pattern_name}, Pattern Timeframe: ${pattern.timeframe}`}
                  />
                );
              }
              return null;
            }}
          />
          <ReferenceLine y={0} stroke="#000" />
        </LineChart>
      </ResponsiveContainer>
      <div className="timeframe-buttons">
        <button
          className={
            timeframe === 0
              ? "active-timeframe-button"
              : "inactive-timeframe-button"
          }
          onClick={() => setTimeframe(0)}
        >
          1D
        </button>
        <button
          className={
            timeframe === 1
              ? "active-timeframe-button"
              : "inactive-timeframe-button"
          }
          onClick={() => setTimeframe(1)}
        >
          1W
        </button>
        <button
          className={
            timeframe === 2
              ? "active-timeframe-button"
              : "inactive-timeframe-button"
          }
          onClick={() => setTimeframe(2)}
        >
          1M
        </button>
        <button
          className={
            timeframe === 3
              ? "active-timeframe-button"
              : "inactive-timeframe-button"
          }
          onClick={() => setTimeframe(3)}
        >
          3M
        </button>
        <button
          className={
            timeframe === 6
              ? "active-timeframe-button"
              : "inactive-timeframe-button"
          }
          onClick={() => setTimeframe(6)}
        >
          YTD
        </button>
        <button
          className={
            timeframe === 4
              ? "active-timeframe-button"
              : "inactive-timeframe-button"
          }
          onClick={() => setTimeframe(4)}
        >
          1Y
        </button>
        <button
          className={
            timeframe === 5
              ? "active-timeframe-button"
              : "inactive-timeframe-button"
          }
          onClick={() => setTimeframe(5)}
        >
          5Y
        </button>
      </div>
    </div>
  );
}

export default StockChart;
