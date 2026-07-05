import React, { useState } from 'react';
import { MessageSquare, X, ExternalLink } from 'lucide-react';
import { ChatInterface } from './ChatInterface';
import './ChatWidget.css';

interface ChatWidgetProps {
  onNavigateToFAQ: () => void;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({ onNavigateToFAQ }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="chat-widget-container">
      {isOpen ? (
        <div className="chat-widget-window">
          <div className="chat-widget-header">
            <div className="header-info">
              <h3>SafeX Assistant</h3>
              <span className="status">Online</span>
            </div>
            <button className="close-btn" onClick={() => setIsOpen(false)}>
              <X size={20} />
            </button>
          </div>
          
          <div className="chat-widget-body">
            <ChatInterface />
          </div>
          
          <div className="chat-widget-footer" onClick={onNavigateToFAQ}>
            <span>Need more help? View all FAQs</span>
            <ExternalLink size={14} />
          </div>
        </div>
      ) : (
        <button className="chat-widget-toggle" onClick={() => setIsOpen(true)}>
          <MessageSquare size={24} />
        </button>
      )}
    </div>
  );
};
