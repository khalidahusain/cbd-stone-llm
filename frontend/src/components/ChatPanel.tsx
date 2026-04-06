import { useCallback } from "react";
import { useChatState, useChatDispatch } from "../context/ChatContext";
import { sendChatMessage } from "../api/client";
import MessageList from "./chat/MessageList";
import ChatInput from "./chat/ChatInput";
import TypingIndicator from "./chat/TypingIndicator";
import ConfirmButton from "./chat/ConfirmButton";

export default function ChatPanel() {
  const state = useChatState();
  const dispatch = useChatDispatch();

  const handleSend = useCallback(
    async (message: string) => {
      dispatch({ type: "SEND_MESSAGE", message });
      try {
        const response = await sendChatMessage({
          session_id: state.session_id ?? undefined,
          message,
        });
        dispatch({
          type: "RECEIVE_RESPONSE",
          session_id: response.session_id,
          assistant_message: response.message,
          prediction: response.prediction,
          conversation_phase: response.conversation_phase,
          extracted_features: response.extracted_features,
          missing_required: response.missing_required,
          turn_number: response.turn_number,
        });
      } catch (err) {
        dispatch({
          type: "SET_ERROR",
          error: err instanceof Error ? err.message : "Unknown error",
        });
      }
    },
    [state.session_id, dispatch]
  );

  const handleConfirm = useCallback(() => {
    handleSend("confirm");
  }, [handleSend]);

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={state.messages} />
      {state.loading && <TypingIndicator />}
      {state.conversation_phase === "awaiting_confirmation" && !state.loading && (
        <ConfirmButton onConfirm={handleConfirm} />
      )}
      {state.error && (
        <div className="px-4 pb-2 text-red-600 text-xs">Error: {state.error}</div>
      )}
      <ChatInput onSend={handleSend} disabled={state.loading} />
    </div>
  );
}
