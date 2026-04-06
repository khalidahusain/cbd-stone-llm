import type { PredictionResult } from "../../types/api";

const TIER_COLORS: Record<string, string> = {
  low: "text-green-600",
  intermediate: "text-amber-600",
  high: "text-orange-600",
  very_high: "text-red-600",
};

const TIER_LABELS: Record<string, string> = {
  low: "Low Risk",
  intermediate: "Intermediate Risk",
  high: "High Risk",
  very_high: "Very High Risk",
};

export default function ProbabilityDisplay({ prediction }: { prediction: PredictionResult | null }) {
  if (!prediction) {
    return (
      <div className="text-center py-3">
        <p className="text-gray-400 text-sm">Awaiting clinical data...</p>
      </div>
    );
  }

  const color = TIER_COLORS[prediction.risk_tier] || "text-gray-600";
  const label = TIER_LABELS[prediction.risk_tier] || prediction.risk_tier;

  return (
    <div className="text-center py-2">
      <p className={`text-3xl font-bold ${color}`}>{prediction.probability}%</p>
      <p className={`text-sm font-semibold ${color}`}>{label}</p>
    </div>
  );
}
