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
        // Store the data in a global state or in local storage here
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
    console.log(timeout)
    fetchPattern(id, timeout);
  });
};

fetchData();
