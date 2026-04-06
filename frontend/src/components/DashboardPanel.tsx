import { useChatState } from "../context/ChatContext";
import ProbabilityDisplay from "./dashboard/ProbabilityDisplay";
import GuidanceBar from "./dashboard/GuidanceBar";
import CostTable from "./dashboard/CostTable";
import InterpretationGuide from "./dashboard/InterpretationGuide";
import Abbreviations from "./dashboard/Abbreviations";
import CholangitisOverlay from "./dashboard/CholangitisOverlay";

export default function DashboardPanel() {
  const { prediction } = useChatState();

  return (
    <div className="h-full overflow-y-auto p-3 space-y-3">
      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center">
        Clinical Dashboard
      </h2>

      <ProbabilityDisplay prediction={prediction} />

      {prediction && (
        <>
          {/* Guidance bar with optional cholangitis overlay */}
          <div className="relative">
            <GuidanceBar probability={prediction.probability} />
            {prediction.cholangitis_flag && prediction.cholangitis_message && (
              <CholangitisOverlay message={prediction.cholangitis_message} />
            )}
          </div>

          {/* Recommended intervention */}
          <div className="text-center">
            <p className="text-xs text-gray-500">Suggested next step in management</p>
            <p className="text-sm font-bold text-gray-800">
              {prediction.recommended_intervention}
            </p>
          </div>

          <CostTable costs={prediction.cost_estimates} />
        </>
      )}

      {/* Always visible static panels */}
      <div className="border-t border-gray-200 pt-2">
        <InterpretationGuide />
      </div>
      <div className="border-t border-gray-200 pt-2">
        <Abbreviations />
      </div>
    </div>
  );
}
