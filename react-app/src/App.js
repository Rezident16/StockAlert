import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { Route, Switch } from "react-router-dom";
import LoginFormPage from "./components/LoginFormPage";
import { authenticate } from "./store/session";
import Navigation from "./components/Navigation";
import StockNews from "./components/Stock/StockNews";
import StockPatterns from "./components/Stock/StockPatterns";

function App() {
  const dispatch = useDispatch();
  const [isLoaded, setIsLoaded] = useState(false);
  useEffect(() => {
    dispatch(authenticate()).then(() => setIsLoaded(true));
  }, [dispatch]);
  
  useEffect(() => {
    const fetchData = () => {
      fetch('http://localhost:5000/api/stocks/get_patterns')
        .then(response => response.json())
        .then(data => {
          setTimeout(fetchData, 20 * 60 * 1000);
        })
        .catch(error => {
          setTimeout(fetchData, 20 * 60 * 1000);
        });
    };
      fetchData();
  }, []);

  return (
    <>
      <Navigation isLoaded={isLoaded} />
      {isLoaded && (
        <Switch>
          <Route path="/login">
            <LoginFormPage />
          </Route>
          <Route path="/stock/:id/news">
            <StockNews />
          </Route>
          <Route path="/stock/:id/patterns">
            <StockPatterns />
          </Route>
        </Switch>
      )}
    </>
  );
}

export default App;
