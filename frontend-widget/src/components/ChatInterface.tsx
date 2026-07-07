import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './ChatInterface.css';

export interface Message {
  id: string;
  text: string;
  isBot: boolean;
}

interface ChatInterfaceProps {
  className?: string;
  hideQuickReplies?: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '', hideQuickReplies = false }) => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'Hello! I am the SafeX AI assistant. How can I help you today?', isBot: true }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const sessionIdRef = useRef<string>(Math.random().toString(36).substring(2, 15));

  const faqs = [
    'Which countries do you operate in?',
    'What cybersecurity services do you offer?',
    'What are your support hours?'
  ];

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const text = typeof textToSend === 'string' ? textToSend : inputValue;
    if (!text.trim() || isLoading) return;

    const newUserMsg: Message = { id: Date.now().toString(), text: text, isBot: false };
    setMessages(prev => [...prev, newUserMsg]);
    if (typeof textToSend !== 'string') {
      setInputValue('');
    }

    const botMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: botMsgId, text: '', isBot: true }]);
    setIsLoading(true);

    // Cancel any previous in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    // 5-minute timeout for slow model loading
    const timeoutId = setTimeout(() => controller.abort(), 300000);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-Id': 'default-tenant'
        },
        body: JSON.stringify({
          query: text,
          user_id: 'local-test-user',
          session_id: sessionIdRef.current
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No readable stream');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunkValue = decoder.decode(value, { stream: true });
          setMessages(prev => prev.map(msg =>
            msg.id === botMsgId ? { ...msg, text: msg.text + chunkValue } : msg
          ));
        }
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      let errorText = 'Error connecting to the chat service. Ensure backend and Ollama are running.';
      if (error.name === 'AbortError') {
        errorText = 'Request timed out. The model may still be loading — please try again in a moment.';
      }
      setMessages(prev => prev.map(msg =>
        msg.id === botMsgId ? { ...msg, text: errorText } : msg
      ));
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  return (
    <div className={`chat-interface ${className}`}>
      <div className="chat-messages" ref={messagesContainerRef}>
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message-wrapper ${msg.isBot ? 'bot' : 'user'}`}>
            <div className="chat-avatar">
              {msg.isBot ? <Bot size={18} /> : <User size={18} />}
            </div>
            <div className="chat-bubble">
              {msg.text ? (
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              ) : (isLoading && msg.isBot ? (
                <span className="typing-indicator">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </span>
              ) : null)}
            </div>
          </div>
        ))}

        {!hideQuickReplies && messages.length === 1 && (
          <div className="faq-quick-replies">
            {faqs.map((faq, idx) => (
              <button
                key={idx}
                className="faq-quick-reply-btn"
                onClick={() => handleSend(faq)}
              >
                {faq}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          placeholder={isLoading ? "Waiting for response..." : "Type your message..."}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          disabled={isLoading}
        />
        <button className="send-btn" onClick={() => handleSend()} disabled={isLoading}>
          {isLoading ? <Loader2 size={18} className="spin-icon" /> : <Send size={18} />}
        </button>
      </div>
    </div>
  );
};
