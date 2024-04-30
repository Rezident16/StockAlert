export const fetchData = () => {
    fetch('http://localhost:5000/api/stocks/get_patterns')
      .then(response => response.json())
      .then(data => {
        // Store the data in a global state or in local storage here
        setTimeout(fetchData, 20 * 60 * 1000);
      })
      .catch(error => {
        setTimeout(fetchData, 20 * 60 * 1000);
      });
  };
  
  fetchData(); 
