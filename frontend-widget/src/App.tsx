import { useState } from 'react'
import { Header } from './components/Header'
import { ChatWidget } from './components/ChatWidget'
import { FAQScreen } from './components/FAQScreen'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState<'home' | 'faq'>('home')

  if (currentView === 'faq') {
    return <FAQScreen onNavigateHome={() => setCurrentView('home')} />
  }

  return (
    <div className="app-container mock-website">
      <Header onNavigateHome={() => setCurrentView('home')} />
      
      {/* Mock content representing the SafeX website */}
      <main className="mock-hero">
        <h1>About <span>SafeX</span> Solutions</h1>
        <p>
          <strong>SafeX Solutions</strong> is a global, full service technology and digital solutions company delivering innovative IT services, cybersecurity, marketing, and creative media solutions to businesses across more than 15 countries worldwide.
        </p>
        <p>
          At SafeX Solutions, we specialize in web development, network infrastructure, cloud solutions, and cybersecurity services designed to keep your business connected, protected, and future-ready.
        </p>
      </main>

      {/* The floating chatbot widget */}
      <ChatWidget onNavigateToFAQ={() => setCurrentView('faq')} />
    </div>
  )
}

export default App
