import React, { useEffect } from 'react';
import { Header } from './Header';
import { ChatInterface } from './ChatInterface';
import { HelpCircle, Shield, Globe, Clock } from 'lucide-react';
import './FAQScreen.css';

interface FAQScreenProps {
  onNavigateHome: () => void;
  currentView?: 'home' | 'faq';
}

export const FAQScreen: React.FC<FAQScreenProps> = ({ onNavigateHome, currentView }) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const faqs = [
    {
      icon: <Globe size={20} />,
      question: 'Which countries do you operate in?',
      answer: 'We deliver innovative IT and cybersecurity solutions to businesses across more than 15 countries worldwide.'
    },
    {
      icon: <Shield size={20} />,
      question: 'What cybersecurity services do you offer?',
      answer: 'We specialize in network infrastructure, cloud solutions, and comprehensive cybersecurity designed to keep your business connected and protected.'
    },
    {
      icon: <Clock size={20} />,
      question: 'What are your support hours?',
      answer: 'Our dedicated support team is available 24/7 to ensure your digital presence remains secure and competitive.'
    },
    {
      icon: <HelpCircle size={20} />,
      question: 'How can I reset my password?',
      answer: 'You can reset your password by clicking on the "Forgot Password" link on the login page.'
    }
  ];

  return (
    <div className="faq-screen">
      <Header onNavigateHome={onNavigateHome} currentView={currentView} />
      
      <main className="faq-main-content">
        <div className="faq-container">
          <div className="faq-sidebar">
            <div className="faq-header">
              <h2>Frequently Asked Questions</h2>
              <p>Find quick answers or chat with our AI assistant for personalized help.</p>
            </div>
            
            <div className="faq-list">
              {faqs.map((faq, idx) => (
                <div key={idx} className="faq-item">
                  <div className="faq-icon-wrapper">
                    {faq.icon}
                  </div>
                  <div className="faq-text">
                    <h4>{faq.question}</h4>
                    <p>{faq.answer}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="faq-chat-section">
            <div className="faq-chat-header">
              <h3>Ask SafeX AI</h3>
              <p>Didn't find what you're looking for? Just ask!</p>
            </div>
            <div className="faq-chat-wrapper">
              <ChatInterface className="full-height-chat" hideQuickReplies={true} />
            </div>
          </div>
        </div>
        
        <div className="about-safex-section">
          <h1>About <span>SafeX</span> Solutions</h1>
          <p>
            <strong>SafeX Solutions</strong> is a global, full service technology and digital solutions company delivering innovative IT services, cybersecurity, marketing, and creative media solutions to businesses across more than 15 countries worldwide.
          </p>
          <p>
            At SafeX Solutions, we specialize in web development, network infrastructure, cloud solutions, and cybersecurity services designed to keep your business connected, protected, and future-ready.
          </p>
        </div>
      </main>
    </div>
  );
};
