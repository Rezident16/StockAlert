const GET_STOCK = "stock/GET_STOCK";

const getStock = (stock) => ({
    type: GET_STOCK,
    stock,
});

export const getStockThunk = (id) => async (dispatch) => {
    const response = await fetch(`/api/stocks/${id}`);
    if (response.ok) {
        const data = await response.json();
        dispatch(getStock(data));
    }
}

const initialState = { stock: {} };

export default function stockReducer(state = initialState, action) {
    switch (action.type) {
        case 'stock/GET_STOCK':
          return action.stock;
        default:
          return state;
      }
}
