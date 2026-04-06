import { useState, useEffect } from "react";
import { useChatState } from "../context/ChatContext";
import ProbabilityDisplay from "./dashboard/ProbabilityDisplay";
import GuidanceBar from "./dashboard/GuidanceBar";
import CostTable from "./dashboard/CostTable";
import InterpretationGuide from "./dashboard/InterpretationGuide";
import Abbreviations from "./dashboard/Abbreviations";
import CholangitisOverlay from "./dashboard/CholangitisOverlay";
import { CollapsibleSection } from "./CollapsibleSection";

const TIER_BG_COLORS: Record<string, string> = {
  low: "bg-green-50 border-green-200",
  intermediate: "bg-amber-50 border-amber-200",
  high: "bg-orange-50 border-orange-200",
  very_high: "bg-red-50 border-red-200",
};

const TIER_TEXT_COLORS: Record<string, string> = {
  low: "text-green-700",
  intermediate: "text-amber-700",
  high: "text-orange-700",
  very_high: "text-red-700",
};

const TIER_LABELS: Record<string, string> = {
  low: "Low Risk",
  intermediate: "Intermediate Risk",
  high: "High Risk",
  very_high: "Very High Risk",
};

export default function MobileDashboard() {
  const { prediction } = useChatState();
  const [dashboardExpanded, setDashboardExpanded] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (prediction && !mounted) {
      const id = setTimeout(() => setMounted(true), 0);
      return () => clearTimeout(id);
    }
  }, [prediction, mounted]);

  if (!prediction) {
    return null;
  }

  const bgColor = TIER_BG_COLORS[prediction.risk_tier] || "bg-gray-50 border-gray-200";
  const textColor = TIER_TEXT_COLORS[prediction.risk_tier] || "text-gray-700";
  const tierLabel = TIER_LABELS[prediction.risk_tier] || prediction.risk_tier;

  return (
    <div
      className={`transition-all duration-300 ${
        mounted ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2"
      }`}
    >
      {/* Collapsible header */}
      <button
        type="button"
        className={`w-full flex items-center justify-between px-3 py-2 rounded-lg border ${bgColor}`}
        onClick={() => setDashboardExpanded((prev) => !prev)}
        aria-expanded={dashboardExpanded}
      >
        <div className="text-left">
          <p className={`text-sm font-bold ${textColor}`}>
            {prediction.probability}% &mdash; {tierLabel}
          </p>
          <p className="text-[10px] text-gray-500">Tap to expand/collapse</p>
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className={`w-4 h-4 ${textColor} transition-transform duration-200 ${
            dashboardExpanded ? "rotate-90" : ""
          }`}
        >
          <path
            fillRule="evenodd"
            d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {/* Expanded content */}
      <div
        className={`overflow-hidden transition-all duration-200 ${
          dashboardExpanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="p-3 space-y-3 bg-white border border-gray-200 rounded-b-lg">
          <ProbabilityDisplay prediction={prediction} />

          <div className="relative">
            <GuidanceBar probability={prediction.probability} />
            {prediction.cholangitis_flag && prediction.cholangitis_message && (
              <CholangitisOverlay message={prediction.cholangitis_message} />
            )}
          </div>

          <div className="text-center">
            <p className="text-xs text-gray-500">Suggested next step in management</p>
            <p className="text-sm font-bold text-gray-800">
              {prediction.recommended_intervention}
            </p>
          </div>

          <CollapsibleSection title="Cost-Weighted Interventions">
            <CostTable costs={prediction.cost_estimates} />
          </CollapsibleSection>

          <CollapsibleSection title="Interpretation Guide">
            <InterpretationGuide />
          </CollapsibleSection>

          <CollapsibleSection title="Abbreviations">
            <Abbreviations />
          </CollapsibleSection>
        </div>
      </div>
    </div>
  );
}
