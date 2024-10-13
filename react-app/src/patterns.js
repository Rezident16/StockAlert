export const fetchData = () => {
  const timeframes = {
    1: 900000, // 15 minutes
    2: 1800000, // 30 minutes
    3: 3600000, // 1 hour
    4: 86400000, // 1 day
    5: 604800000, // 1 week
  };

  const fetchPattern = (id, timeout) => {
    fetch(`/api/stocks/get_patterns/${id}`)
      .then((response) => response.json())
      .then((data) => {
        // Process the data here
      })
      .catch((error) => {
        console.error(error);
      })
      .finally(() => {
        setTimeout(() => fetchPattern(id, timeout), timeout);
      });
  };

  // Loop through the timeframes object and call fetchPattern
  Object.keys(timeframes).forEach((id) => {
    const timeout = timeframes[id];
    fetchPattern(id, timeout);
  });
};

export const fetchNewsData = () => {
  const fetchNews = () => {
    fetch("/api/stocks/news")
      .then((response) => response.json())
      .then((data) => {
        // Process the data here
        console.log(data); // Example processing
      })
      .catch((error) => {
        console.error(error);
      })
      .finally(() => {
        setTimeout(fetchNews, 3600000); // Fetch news every hour
      });
  };

  fetchNews();
};


