import React, { useState, useEffect } from "react";
import patternConversion from "../patternConversion";

export const fetchBars = async ({setBarset, stockId, timeframeId}) => {
    const response = await fetch(`/api/charts/${stockId}/bars/${timeframeId}`);
    const data = await response.json();
    const barsWithDateObjects = data.map((bar) => ({
      ...bar,
      date: new Date(bar.date).toLocaleString(),
    }));
    setBarset(barsWithDateObjects);
}

export const fetchChartPatterns = async ({setPatterns, stockId, timeframeId}) => {
  const response = await fetch(`/api/charts/${stockId}/patterns/${timeframeId}`);
  const data = await response.json();
  const patterns = data.patterns.map((pattern) => ({
    ...pattern,
    date: new Date(Number(pattern['milliseconds'])).toLocaleString(),
    pattern_name: patternConversion(pattern['pattern_name']),
}));
    setPatterns(patterns);
}
