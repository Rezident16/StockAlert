const GET_STOCK_PRICE = "stock/GET_STOCK_PRICE";

const getStockPrice = (stockPrice) => ({
    type: GET_STOCK_PRICE,
    stockPrice,
});

export const getStockPriceThunk = (id) => async (dispatch) => {
    const response = await fetch(`/api/stocks/${id}/stock_price`);
    if (response.ok) {
        const data = await response.json();
        dispatch(getStockPrice(data));
    }
}

const initialState = { stockPrice: [] };

export default function stockPriceReducer(state = initialState, action) {
    switch (action.type) {
        case 'stock/GET_STOCK_PRICE':
          return {
            price: action.stockPrice.toFixed(2)
          };
        default:
          return state;
      }
}
