const GET_STOCK_NEWS = "stock/GET_STOCK_NEWS";

const getStockNews = (news) => ({
    type: GET_STOCK_NEWS,
    news,
});

export const getStockNewsThunk = (id) => async (dispatch) => {
    const response = await fetch(`/api/stocks/${id}/news`);
    if (response.ok) {
        const data = await response.json();
        dispatch(getStockNews(data));
    }
}

const initialState = { news: [] };

export default function stockReducer(state = initialState, action) {
    switch (action.type) {
        case 'stock/GET_STOCK_NEWS':
          return {
            ...state,
            news: [...action.news]
          };
        default:
          return state;
      }
}
