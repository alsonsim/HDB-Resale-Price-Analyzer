import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm AgentForge, your HDB resale market assistant. Ask me anything about HDB resale prices, trends, or whether a flat is fairly priced. Try something like:\n\n" +
        '- "What\'s the average price of a 4-room flat in Tampines?"\n' +
        '- "Is $550K fair for a 4-room in Sengkang?"\n' +
        '- "Compare Punggol vs Sengkang for 5-room flats"',
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(userMessage, sessionId);
      setSessionId(response.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please check the backend connection and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Chat</h1>
        <p className="text-gray-500">
          Ask the AI agent about the HDB resale market
        </p>
      </div>

      <div className="flex-1 card overflow-y-auto mb-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === "user"
                  ? "bg-primary-600 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span className="animate-pulse">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about HDB resale prices..."
          className="input-field flex-1"
          disabled={loading}
        />
        <button type="submit" className="btn-primary" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
