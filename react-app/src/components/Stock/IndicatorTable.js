import { useSelector } from "react-redux";

const STATUS_STYLES = {
  good: "bg-bullish/15 text-bullish",
  bad: "bg-bearish/15 text-bearish",
  neutral: "bg-amber-100 text-amber-700",
};

const STATUS_LABELS = {
  good: "Good",
  bad: "Bad",
  neutral: "Neutral",
};

function IndicatorTable() {
  const signal = useSelector((state) => state.signal.signal);
  const indicators = signal?.indicators || [];

  if (indicators.length === 0) return null;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm md:p-5">
      <h2 className="mb-3 text-base font-semibold text-gray-800">Indicators</h2>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-gray-400">
              <th className="border-b border-gray-200 px-2 py-1.5 font-medium">Indicator</th>
              <th className="border-b border-gray-200 px-2 py-1.5 font-medium">Value</th>
              <th className="border-b border-gray-200 px-2 py-1.5 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {indicators.map((indicator) => (
              <tr key={indicator.name}>
                <td className="whitespace-nowrap border-b border-gray-100 px-2 py-2 font-medium text-gray-700">
                  {indicator.name}
                </td>
                <td className="whitespace-nowrap border-b border-gray-100 px-2 py-2 text-gray-600">
                  {indicator.value}
                </td>
                <td className="whitespace-nowrap border-b border-gray-100 px-2 py-2">
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${STATUS_STYLES[indicator.status] || STATUS_STYLES.neutral}`}
                  >
                    {STATUS_LABELS[indicator.status] || indicator.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default IndicatorTable;
