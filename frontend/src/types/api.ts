export interface CostEstimate {
  intervention: string;
  cost: number;
}

export interface PredictionResult {
  probability: number;
  risk_tier: "low" | "intermediate" | "high" | "very_high";
  recommended_intervention: string;
  cost_estimates: CostEstimate[];
  cholangitis_flag: boolean;
  cholangitis_message: string | null;
  imputed_fields: string[];
}

export interface ChatRequest {
  session_id?: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  extracted_features: Record<string, unknown>;
  prediction: PredictionResult | null;
  conversation_phase: ConversationPhase;
  missing_required: string[];
  turn_number: number;
}

export type ConversationPhase = "collecting" | "awaiting_confirmation" | "confirmed";
