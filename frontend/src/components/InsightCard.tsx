import type { AnalysisResult } from "../api/client";

interface InsightCardProps {
  analysis: AnalysisResult;
}

export default function InsightCard({ analysis }: InsightCardProps) {
  const badgeClass = analysis.is_fair
    ? "badge-fair"
    : analysis.price_vs_median_pct > 0
      ? "badge-overpriced"
      : "badge-below";

  const badgeText = analysis.is_fair
    ? "Fair Price"
    : analysis.price_vs_median_pct > 0
      ? "Above Market"
      : "Below Market";

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">AI Price Analysis</h3>
        <span className={badgeClass}>{badgeText}</span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-500">Fair Range</div>
          <div className="font-semibold">
            ${analysis.fair_price_range[0].toLocaleString()} —{" "}
            ${analysis.fair_price_range[1].toLocaleString()}
          </div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-500">vs Median</div>
          <div
            className={`font-semibold ${
              analysis.price_vs_median_pct > 5
                ? "text-red-600"
                : analysis.price_vs_median_pct < -5
                  ? "text-green-600"
                  : "text-gray-900"
            }`}
          >
            {analysis.price_vs_median_pct > 0 ? "+" : ""}
            {analysis.price_vs_median_pct}%
          </div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-500">Comparables</div>
          <div className="font-semibold">
            {analysis.comparable_transactions.length} txns
          </div>
        </div>
      </div>

      <div className="prose prose-sm max-w-none">
        <p className="text-gray-600 text-sm mb-3">{analysis.summary}</p>
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
          <div className="text-sm font-medium text-blue-800 mb-1">
            AI Insight
          </div>
          <div className="text-sm text-blue-900 whitespace-pre-wrap">
            {analysis.ai_insight}
          </div>
        </div>
      </div>
    </div>
  );
}
