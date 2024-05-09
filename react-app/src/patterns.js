export const fetchData = () => {
  const timeframes = {
    1: "900000",
    2: "1800000",
    3: "3600000",
    4: "86400000",
    5: "604800000",
  };

  const fetchPattern = (id, timeout) => {
    fetch(`http://localhost:5000/api/stocks/get_patterns/${id}`)
      .then((response) => response.json())
      .then((data) => {
        
      })
      .catch((error) => {
        console.error(error);
      })
      .finally(() => {
        setTimeout(() => fetchPattern(id, timeout), timeout * 60 * 1000);
      });
  };

  Object.keys(timeframes).forEach((id) => {
    const timeout = parseInt(timeframes[id]);
    fetchPattern(id, timeout);
  });
};

export const fetchNewsData = () => {
  const fetchNews = () => {
    fetch("http://localhost:5000/api/stocks/get_all_news")
      .then((response) => response.json())
      .then((data) => {
        
      })
      .catch((error) => {
        console.error(error);
      })
      .finally(() => {
        setTimeout(fetchNews, 3600000);
      });
  }}

fetchData();
