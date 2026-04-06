import { useEffect, useRef, type ReactNode } from "react";
import type { ChatMessage } from "../../context/ChatContext";

function formatBold(text: string): ReactNode[] {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
  );
}

export default function MessageList({ messages }: { messages: ChatMessage[] }) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.length === 0 && (
        <p className="text-gray-400 text-center mt-8 text-sm">
          Describe a patient case to get started.
        </p>
      )}
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            className={`max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
              msg.role === "user"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {formatBold(msg.content)}
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
