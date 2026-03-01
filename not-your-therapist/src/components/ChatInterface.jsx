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

    const assistantTempId = `assistant-temp-${Date.now()}`
    // add placeholder assistant message that we'll update as chunks arrive
    setMessages(prev => [...prev, { id: assistantTempId, text: '', sender: 'therapist', timestamp: new Date() }])

    let convIdSet = conversationId
    try {
      await sendMessage(text, conversationId, ({ event, data }) => {
        // data is expected to be the ChatResponse-like object
        if (!data) return
        // set conversation id from first chunk if present
        if (!convIdSet && data.conversation_id) {
          convIdSet = data.conversation_id
          setConversationId(convIdSet)
        }

        if (event === 'message') {
          const chunk = data.assistant_message?.content || ''
          setMessages(prev => prev.map(m => m.id === assistantTempId ? { ...m, text: (m.text || '') + chunk } : m))
        } else if (event === 'done') {
          const finalText = typeof data === 'string' ? data : (data.assistant_message?.content || '')
          setMessages(prev => prev.map(m => m.id === assistantTempId ? { ...m, text: finalText, timestamp: new Date() } : m))
          setIsTyping(false)
        }
      })
    } catch (err) {
      setError(err.message || 'Failed to send message')
      // remove user message and temp assistant message on error
      setMessages(prev => prev.filter(m => m.id !== userMessage.id && m.id !== assistantTempId))
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
