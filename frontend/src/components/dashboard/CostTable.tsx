import type { CostEstimate } from "../../types/api";

function formatCurrency(value: number): string {
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function CostTable({ costs }: { costs: CostEstimate[] }) {
  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
        Cost-Weighted Interventions
      </h3>
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-1 font-semibold text-gray-600">Intervention</th>
            <th className="text-right py-1 font-semibold text-gray-600">Expected Cost</th>
          </tr>
        </thead>
        <tbody>
          {costs.map((c) => (
            <tr key={c.intervention} className="border-b border-gray-100">
              <td className="py-1 text-gray-700 font-medium">{c.intervention}</td>
              <td className="py-1 text-right text-gray-700">{formatCurrency(c.cost)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
