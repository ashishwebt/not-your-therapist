import { useState, useRef, useEffect } from 'react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import { sendMessage } from '../services/api'
import '../styles/ChatInterface.css'

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 'intro',
      text: "Hello! I'm here to listen. What's on your mind today?",
      sender: 'therapist',
      timestamp: new Date(Date.now() - 5 * 60000)
    }
  ])
  const [isTyping, setIsTyping] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (text) => {
    const userMessage = {
      id: `user-${Date.now()}`,
      text: text,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages([...messages, userMessage])
    setIsTyping(true)
    setError(null)

    try {
      const response = await sendMessage(text, conversationId)

      // Update conversation ID on first message
      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      const therapistMessage = {
        id: `assistant-${Date.now()}`,
        text: response.assistant_message.content,
        sender: 'therapist',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, therapistMessage])
    } catch (err) {
      setError(err.message || 'Failed to send message')
      // Remove user message if error occurs
      setMessages(prev => prev.filter(m => m.id !== userMessage.id))
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>Not Your Therapist</h1>
        <p className="subtitle">Your personal companion for reflection</p>
      </div>

      <div className="chat-messages">
        {error && (
          <div className="error-message">
            <span>{error}</span>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isTyping && (
          <div className="message therapist-message">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSendMessage={handleSendMessage} disabled={isTyping} />
    </div>
  )
}

export default ChatInterface
