import { useEffect, useState, Fragment } from 'react';

const FinvizData = ({ id }) => {
    const [stockData, setStockData] = useState(null);
    const [columns, setColumns] = useState(6); // Default to 6 columns
    const [isOpen, setIsOpen] = useState(true);

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
            <button
                type="button"
                onClick={() => setIsOpen((open) => !open)}
                className="mb-3 flex w-full items-center justify-between text-left"
            >
                <h2 className="text-base font-semibold text-gray-800">Finviz Stock Data</h2>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    className={`h-5 w-5 text-gray-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
                >
                    <path
                        fillRule="evenodd"
                        d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                        clipRule="evenodd"
                    />
                </svg>
            </button>
            {isOpen && (stockData ? (
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
            ))}
        </div>
    );
};

export default FinvizData;
