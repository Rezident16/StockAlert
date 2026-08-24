const GET_STOCK_SIGNAL = "stock/GET_STOCK_SIGNAL";

const getStockSignal = (signal) => ({
    type: GET_STOCK_SIGNAL,
    signal,
});

export const getStockSignalThunk = (id, timeframe) => async (dispatch) => {
    const query = timeframe ? `?timeframe=${encodeURIComponent(timeframe)}` : "";
    const response = await fetch(`/api/stocks/${id}/signal${query}`);
    if (response.ok) {
        const data = await response.json();
        dispatch(getStockSignal(data));
    }
}

const initialState = { signal: null };

export default function signalReducer(state = initialState, action) {
    switch (action.type) {
        case GET_STOCK_SIGNAL:
          return { signal: action.signal };
        default:
          return state;
      }
}
