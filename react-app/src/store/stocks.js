const GET_STOCKS = "stock/GET_STOCKS";

const getStocks = (stocks) => ({
    type: GET_STOCKS,
    stocks,
});

export const getStocksThunk = () => async (dispatch) => {
    const response = await fetch(`/api/stocks`);
    if (response.ok) {
        const data = await response.json();
        dispatch(getStocks(data));
    }
}

const initialState = { stocks: [] };

export default function stockReducer(state = initialState, action) {
    switch (action.type) {
        case 'stock/GET_STOCKS':
          return {
            ...state,
            stocks: [...action.stocks]
          };
        default:
          return state;
      }
}
