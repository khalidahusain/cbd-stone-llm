import type { ChatRequest, ChatResponse } from "../types/api";

const API_BASE = "http://10.17.67.98:451";

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `API error: ${response.status}`);
  }
  return response.json();
}
