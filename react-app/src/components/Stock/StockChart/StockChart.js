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

const TIMEFRAMES = [
  { id: 0, label: "1D" },
  { id: 1, label: "1W" },
  { id: 2, label: "1M" },
  { id: 3, label: "3M" },
  { id: 6, label: "YTD" },
  { id: 4, label: "1Y" },
  { id: 5, label: "5Y" },
];

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
    <div className="rounded-xl border border-gray-200 bg-white p-3 shadow-sm md:p-4">
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
      <div className="mt-2 flex flex-wrap justify-center gap-1 sm:justify-start">
        {TIMEFRAMES.map(({ id: tfId, label }) => (
          <button
            key={tfId}
            onClick={() => setTimeframe(tfId)}
            className={
              "rounded-full px-3 py-1 text-xs font-bold transition-colors " +
              (timeframe === tfId
                ? "bg-bullish/15 text-bullish"
                : "text-gray-500 hover:bg-gray-100")
            }
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default StockChart;
