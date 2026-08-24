import { createStore, combineReducers, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';
import session from './session'
import userReducer from './user';
import newsReducer from './news';
import stocksReducer from './stocks';
import patternsReducer from './patterns';
import stockPriceReducer from './stockPrice';
import stockReducer from './stock';
import signalReducer from './signal';

const rootReducer = combineReducers({
  session,
  user: userReducer,
  news: newsReducer,
  stocks: stocksReducer,
  patterns: patternsReducer,
  price: stockPriceReducer,
  stock: stockReducer,
  signal: signalReducer,
});


let enhancer;

if (process.env.NODE_ENV === 'production') {
  enhancer = applyMiddleware(thunk);
} else {
  const logger = require('redux-logger').default;
  const composeEnhancers =
    window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
  enhancer = composeEnhancers(applyMiddleware(thunk, logger));
}

const configureStore = (preloadedState) => {
  return createStore(rootReducer, preloadedState, enhancer);
};

export default configureStore;
