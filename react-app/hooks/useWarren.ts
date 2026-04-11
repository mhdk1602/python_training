/*
 * REACT PATTERN: API integration hook
 *
 * Separating the "Ask Warren" chat logic from the UI component means:
 *   - The chat UI only manages scroll position and input focus
 *   - This hook manages the message list and API round-trips
 *   - You could swap the Anthropic backend for OpenAI by changing one URL
 *
 * The hook returns the full chat history and a submit function.
 * The component never touches fetch() directly.
 */

import { useState, useCallback } from "react";
import { ChatMessage } from "../types";

const API_BASE = "http://localhost:5002";

export function useWarren() {
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const submit = useCallback(
    async (question: string) => {
      if (!question.trim()) return;

      const userMsg: ChatMessage = { role: "user", content: question };
      setHistory((prev) => [...prev, userMsg]);
      setLoading(true);

      try {
        const res = await fetch(`${API_BASE}/ask_warren`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ userQuestion: question }),
        });
        const data = await res.json();
        const warrenMsg: ChatMessage = {
          role: "warren",
          content: data.response ?? "No response from Warren.",
        };
        setHistory((prev) => [...prev, warrenMsg]);
      } catch {
        setHistory((prev) => [
          ...prev,
          { role: "warren", content: "Connection error. Is the Flask API running?" },
        ]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const clear = useCallback(() => {
    setHistory([]);
  }, []);

  return { history, loading, submit, clear };
}
