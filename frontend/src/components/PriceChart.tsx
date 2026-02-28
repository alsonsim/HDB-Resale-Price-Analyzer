import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { TrendPoint } from "../api/client";

interface PriceChartProps {
  data: TrendPoint[];
  town: string;
  flatType?: string | null;
}

function formatPrice(value: number) {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value}`;
}

export default function PriceChart({ data, town, flatType }: PriceChartProps) {
  if (!data.length) {
    return (
      <div className="card text-center text-gray-500 py-12">
        No trend data available. Try syncing data first.
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">
        Price Trend — {town}
        {flatType && ` (${flatType})`}
      </h3>

      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis tickFormatter={formatPrice} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number) => [`$${value.toLocaleString()}`, ""]}
            labelStyle={{ fontWeight: "bold" }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="avg_price"
            name="Avg Price"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="avg_psm"
            name="Avg $/sqm"
            stroke="#00897b"
            strokeWidth={2}
            dot={false}
            yAxisId={1}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 flex gap-4 text-sm text-gray-600">
        <span>Transactions: {data.reduce((s, d) => s + d.transaction_count, 0)}</span>
        <span>
          Period: {data[0]?.month} to {data[data.length - 1]?.month}
        </span>
      </div>
    </div>
  );
}
