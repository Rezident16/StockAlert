import React, { useEffect, useState, Fragment } from 'react';
import './FinvizData.css'; // Import the CSS file for styling

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
            setColumns(Math.floor(width / 300));
        };

        window.addEventListener('resize', updateColumns);
        updateColumns();

        return () => window.removeEventListener('resize', updateColumns);
    }, []);

    return (
        <div className="finviz-container">
            <h1>Finviz Stock Data</h1>
            {stockData ? (
                <table className="finviz-table">
                    <tbody>
                        {(() => {
                            const rows = [];
                            Object.entries(stockData).map(([key, value], index) => {
                                const rowIndex = Math.floor(index / columns);
                                rows[rowIndex] = rows[rowIndex] || [];
                                rows[rowIndex].push(
                                    <Fragment key={index}>
                                        <td className="finviz-cell finviz-key">{key}</td>
                                        <td className="finviz-cell finviz-value">{value}</td>
                                    </Fragment>
                                );
                                return null;
                            });
                            return rows.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {row}
                                </tr>
                            ));
                        })()}
                    </tbody>
                </table>
            ) : (
                <p>No stock data available</p>
            )}
        </div>
    );
};

export default FinvizData;
