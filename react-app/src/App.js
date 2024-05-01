import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { Route, Switch } from "react-router-dom";
import LoginFormPage from "./components/LoginFormPage";
import { authenticate } from "./store/session";
import Navigation from "./components/Navigation";
import StockNews from "./components/Stock/StockNews";
import StockPatterns from "./components/Stock/StockPatterns";
import StockList from "./components/Stock/Stocks";

function App() {
  const dispatch = useDispatch();
  const [isLoaded, setIsLoaded] = useState(false);
  useEffect(() => {
    dispatch(authenticate()).then(() => setIsLoaded(true));
  }, [dispatch]);

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
          <Route path="/stocks">
            <StockList />
          </Route>
        </Switch>
      )}
    </>
  );
}

export default App;
