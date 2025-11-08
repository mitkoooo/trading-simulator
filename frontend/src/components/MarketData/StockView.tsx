import { useStockViewDataStore } from "../../stores/stockViewDataStore";
import { useStock } from "../../hooks/useStock";
import { LineChart } from "@mui/x-charts";

type StockViewProps = {
  className?: string;
};

const StockView = ({ className }: StockViewProps): React.JSX.Element => {
  useStock();
  const selectedStock = useStockViewDataStore((s) => s.selectedStock);

  // Calculate 20-minute range
  const now = new Date();
  const twentyMinutesAgo = new Date(now.getTime() - 20 * 60 * 1000);

  // Filter history to last 20 minutes
  const recentHistory =
    selectedStock?.history.filter(
      (tuple) => new Date(tuple[1]) >= twentyMinutesAgo,
    ) || [];

  // Calculate y-axis range with padding
  const prices = recentHistory.map((tuple) => tuple[0]);
  const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
  const maxPrice = prices.length > 0 ? Math.max(...prices) : 0;
  const padding = (maxPrice - minPrice) * 4 || 1; // 10% padding or 1 if no range

  return (
    <div className={`${className} content-center text-center`}>
      {selectedStock?.symbol ? (
        <div className="h-full w-full p-4">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-2xl font-bold">{selectedStock.symbol}</h2>
            {recentHistory.length > 0 && (
              <div className="text-right">
                <div className="text-3xl font-semibold">
                  ${recentHistory[recentHistory.length - 1][0].toFixed(2)}
                </div>
                <div className="text-sm text-gray-500">
                  {new Date(
                    recentHistory[recentHistory.length - 1][1],
                  ).toLocaleTimeString()}
                </div>
              </div>
            )}
          </div>
          {recentHistory.length > 0 ? (
            <LineChart
              slotProps={{
                legend: { hidden: true },
              }}
              series={[
                {
                  data: prices,
                  label: selectedStock.symbol,
                  color: "#10b981",
                  curve: "linear",
                  showMark: false,
                },
              ]}
              xAxis={[
                {
                  data: recentHistory.map((tuple) => new Date(tuple[1])),
                  scaleType: "time",
                  min: twentyMinutesAgo,
                  max: now,
                  valueFormatter: (date) => {
                    return new Date(date).toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    });
                  },
                },
              ]}
              yAxis={[
                {
                  width: 60,
                  min: minPrice - padding,
                  max: maxPrice + padding,
                  valueFormatter: (value: number) => `$${value}`,
                },
              ]}
              grid={{ vertical: true, horizontal: true }}
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
              sx={{
                width: "100%",
                ".MuiLineElement-root": {
                  strokeWidth: 2,
                },
                ".MuiMarkElement-root": {
                  display: "none",
                },
                // Axis styling
                ".MuiChartsAxis-line": {
                  stroke: "#9ca3af !important", // Gray axis lines
                },
                ".MuiChartsAxis-tick": {
                  stroke: "#9ca3af !important", // Gray tick marks
                },
                ".MuiChartsAxis-tickLabel": {
                  fill: "#6b7280 !important", // Gray axis labels
                },
              }}
              height={500}
            />
          ) : (
            <p className="mt-10 text-gray-500">
              No data in the last 20 minutes
            </p>
          )}
        </div>
      ) : (
        <p className="text-gray-500">
          Select a stock from market watch to start.
        </p>
      )}
    </div>
  );
};

export default StockView;
