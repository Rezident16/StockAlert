import React, { useState, useEffect } from "react";
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

function StockChart({ id }) {
  const [barset, setBarset] = useState([]);

  const fetchBars = async () => {
    // 
    const response = await fetch(`/api/stocks/${id}/bars/4`);
    const data = await response.json();
    const barsWithDateObjects = data.map((bar) => ({
      ...bar,
      date: new Date(bar.date).toLocaleString(),
    }));
    setBarset(barsWithDateObjects);
  };

  useEffect(() => {
    fetchBars();
    const interval = setInterval(fetchBars, 60000);
    return () => clearInterval(interval);
  }, [id]);

  if (barset.length === 0) return null;

  return (
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
        <XAxis dataKey="date" hide={true}/>
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
  );
}

export default StockChart;
