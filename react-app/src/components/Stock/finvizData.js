import { useEffect, useState, Fragment } from 'react';

const FinvizData = ({ id }) => {
    const [stockData, setStockData] = useState(null);
    const [columns, setColumns] = useState(6); // Default to 6 columns

    useEffect(() => {
        const fetchStockData = async () => {
            try {
                const response = await fetch(`/api/stocks/${id}/finviz_stock_data`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                setStockData(data);
            } catch (error) {
                console.error('Error fetching stock data:', error);
            }
        };

        fetchStockData();
    }, [id]);

    useEffect(() => {
        const updateColumns = () => {
            const width = window.innerWidth;
            // Guard against 0 columns on very narrow screens (would divide by
            // zero below).
            setColumns(Math.max(1, Math.floor(width / 300)));
        };

        window.addEventListener('resize', updateColumns);
        updateColumns();

        return () => window.removeEventListener('resize', updateColumns);
    }, []);

    return (
        <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm md:p-5">
            <h2 className="mb-3 text-base font-semibold text-gray-800">Finviz Stock Data</h2>
            {stockData ? (
                <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-xs">
                        <tbody>
                            {(() => {
                                const rows = [];
                                Object.entries(stockData).forEach(([key, value], index) => {
                                    const rowIndex = Math.floor(index / columns);
                                    rows[rowIndex] = rows[rowIndex] || [];
                                    rows[rowIndex].push(
                                        <Fragment key={index}>
                                            <td className="whitespace-nowrap border border-gray-200 px-2 py-1 font-bold text-gray-700">{key}</td>
                                            <td className="whitespace-nowrap border border-gray-200 px-2 py-1 text-gray-600">{value}</td>
                                        </Fragment>
                                    );
                                });
                                return rows.map((row, rowIndex) => (
                                    <tr key={rowIndex}>
                                        {row}
                                    </tr>
                                ));
                            })()}
                        </tbody>
                    </table>
                </div>
            ) : (
                <p className="text-sm text-gray-500">No stock data available</p>
            )}
        </div>
    );
};

export default FinvizData;
