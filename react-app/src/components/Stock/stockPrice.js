
async function getStockPrice(id) {
    const response = await fetch(`/api/stocks/${id}/stock_price`);
    if (response.ok) {
        const data = await response.json();
        return data
    }
}

export default getStockPrice
