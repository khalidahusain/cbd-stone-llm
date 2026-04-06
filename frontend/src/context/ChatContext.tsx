import { createContext, useContext, useReducer, type ReactNode, type Dispatch } from "react";
import type { PredictionResult, ConversationPhase } from "../types/api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface ChatState {
  session_id: string | null;
  messages: ChatMessage[];
  prediction: PredictionResult | null;
  conversation_phase: ConversationPhase;
  extracted_features: Record<string, unknown>;
  missing_required: string[];
  turn_number: number;
  loading: boolean;
  error: string | null;
}

type ChatAction =
  | { type: "SEND_MESSAGE"; message: string }
  | {
      type: "RECEIVE_RESPONSE";
      session_id: string;
      assistant_message: string;
      prediction: PredictionResult | null;
      conversation_phase: ConversationPhase;
      extracted_features: Record<string, unknown>;
      missing_required: string[];
      turn_number: number;
    }
  | { type: "SET_LOADING"; loading: boolean }
  | { type: "SET_ERROR"; error: string }
  | { type: "RESET" };

const initialState: ChatState = {
  session_id: null,
  messages: [],
  prediction: null,
  conversation_phase: "collecting",
  extracted_features: {},
  missing_required: [],
  turn_number: 0,
  loading: false,
  error: null,
};

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "SEND_MESSAGE":
      return {
        ...state,
        messages: [...state.messages, { role: "user", content: action.message }],
        loading: true,
        error: null,
      };
    case "RECEIVE_RESPONSE":
      return {
        ...state,
        session_id: action.session_id,
        messages: [...state.messages, { role: "assistant", content: action.assistant_message }],
        prediction: action.prediction,
        conversation_phase: action.conversation_phase,
        extracted_features: action.extracted_features,
        missing_required: action.missing_required,
        turn_number: action.turn_number,
        loading: false,
      };
    case "SET_LOADING":
      return { ...state, loading: action.loading };
    case "SET_ERROR":
      return { ...state, error: action.error, loading: false };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

const ChatStateContext = createContext<ChatState | null>(null);
const ChatDispatchContext = createContext<Dispatch<ChatAction> | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  return (
    <ChatStateContext.Provider value={state}>
      <ChatDispatchContext.Provider value={dispatch}>
        {children}
      </ChatDispatchContext.Provider>
    </ChatStateContext.Provider>
  );
}

export function useChatState(): ChatState {
  const context = useContext(ChatStateContext);
  if (!context) throw new Error("useChatState must be used within ChatProvider");
  return context;
}

export function useChatDispatch(): Dispatch<ChatAction> {
  const context = useContext(ChatDispatchContext);
  if (!context) throw new Error("useChatDispatch must be used within ChatProvider");
  return context;
}
