import React, { useState, useEffect } from "react";

export const fetchBars = async ({setBarset, stockId, timeframeId}) => {
    const response = await fetch(`/api/charts/${stockId}/bars/${timeframeId}`);
    const data = await response.json();
    console.log(response, 'response')
    const barsWithDateObjects = data.map((bar) => ({
      ...bar,
      date: new Date(bar.date).toLocaleString(),
    }));
    setBarset(barsWithDateObjects);
}
