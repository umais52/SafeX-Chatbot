import { useState } from 'react'
import { Header } from './components/Header'
import { ChatWidget } from './components/ChatWidget'
import { FAQScreen } from './components/FAQScreen'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState<'home' | 'faq'>('home')

  if (currentView === 'faq') {
    return <FAQScreen onNavigateHome={() => setCurrentView('home')} currentView={currentView} />
  }

  return (
    <div className="app-container mock-website">
      <Header onNavigateHome={() => setCurrentView('home')} currentView={currentView} />
      
      {/* Home screen is completely empty per requirements */}
      <main className="mock-hero empty-home" style={{ minHeight: '60vh' }}>
      </main>

      {/* The floating chatbot widget */}
      <ChatWidget onNavigateToFAQ={() => setCurrentView('faq')} />
    </div>
  )
}

export default App
