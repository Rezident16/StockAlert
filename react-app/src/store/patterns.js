const GET_STOCK_PATTERNS = "stock/GET_STOCK_PATTERNS";

const getStockPatterns = (patterns) => ({
    type: GET_STOCK_PATTERNS,
    patterns,
});

export const getStockPatternsThunk = (id) => async (dispatch) => {
    const response = await fetch(`/api/stocks/${id}/patterns`);
    if (response.ok) {
        const data = await response.json();
        dispatch(getStockPatterns(data));
    }
}

const initialState = { patterns: [] };

export default function patternsReducer(state = initialState, action) {
    switch (action.type) {
        case 'stock/GET_STOCK_PATTERNS':
          return {
            ...state,
            patterns: [...action.patterns.patterns]
          };
        default:
          return state;
      }
}
