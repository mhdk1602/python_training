/*
 * REACT PATTERN: Chat UI with auto-scroll and keyboard events
 *
 * Building a chat interface teaches several intermediate React skills:
 *
 *   1. useRef for DOM access: we grab the scroll container and call
 *      scrollTop = scrollHeight after each new message to keep the
 *      latest message visible.
 *
 *   2. Keyboard event handling: Enter key submits the message,
 *      preventing the need to click the send button every time.
 *
 *   3. Conditional rendering: user messages align right (blue),
 *      Warren's responses align left (gray). The same <div> structure
 *      is used for both, with Tailwind classes swapped based on role.
 *
 *   4. Hook integration: all API logic lives in useWarren(). This
 *      component only manages the input field and scroll position.
 */

import React, { useState, useRef, useEffect } from "react";
import { useWarren } from "../hooks/useWarren";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

const AskWarren: React.FC<Props> = ({ isOpen, onClose }) => {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const { history, loading, submit, clear } = useWarren();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  useEffect(() => {
    if (!isOpen) {
      setInput("");
      clear();
    }
  }, [isOpen, clear]);

  if (!isOpen) return null;

  const handleSend = () => {
    if (!input.trim() || loading) return;
    submit(input.trim());
    setInput("");
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content max-w-lg" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/20 text-sm font-bold text-accent">
              W
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Ask Warren</h2>
              <p className="text-xs text-terminal-muted">
                AI-powered investment advisor &middot; Use $TICKER in your question
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-terminal-muted transition-colors hover:bg-white/10 hover:text-white"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div
          ref={scrollRef}
          className="mb-4 flex h-72 flex-col gap-3 overflow-y-auto rounded-lg border border-terminal-border bg-terminal-bg p-3"
        >
          {history.length === 0 && (
            <p className="m-auto text-center text-xs text-terminal-muted">
              Ask about any stock. Example: &quot;What is the outlook for $AAPL?&quot;
            </p>
          )}
          {history.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-xl px-3 py-2 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-accent text-white"
                    : "bg-terminal-card text-terminal-text"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-xl bg-terminal-card px-4 py-2 text-sm text-terminal-muted">
                <span className="inline-flex gap-1">
                  <span className="animate-bounce">.</span>
                  <span className="animate-bounce" style={{ animationDelay: "0.1s" }}>.</span>
                  <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>.</span>
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about a stock using $TICKER..."
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="btn-primary disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AskWarren;
