import { useState, useRef, useEffect } from 'react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import {
  sendMessage,
  getConversations,
  getConversation,
  deleteConversation
} from '../services/api'
import '../styles/ChatInterface.css'

const WELCOME_MESSAGE = {
  id: 'intro',
  text: "Hello! I'm here to listen. What's on your mind today?",
  sender: 'therapist',
  timestamp: new Date(Date.now() - 5 * 60000)
}

function ChatInterface() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [conversations, setConversations] = useState([])
  const [selectedConversationId, setSelectedConversationId] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const data = await getConversations()
      setConversations(data)
    } catch (err) {
      setError(err.message || 'Failed to load conversations')
    }
  }

  const loadConversation = async (conversationId) => {
    if (!conversationId) {
      setMessages([WELCOME_MESSAGE])
      return
    }

    setIsLoadingHistory(true)
    setError(null)

    try {
      const conversation = await getConversation(conversationId)
      const loadedMessages = (conversation.messages || []).map((message, index) => ({
        id: `${message.role}-${conversationId}-${index}`,
        text: message.content,
        sender: message.role === 'assistant' ? 'therapist' : 'user',
        timestamp: new Date()
      }))

      setMessages(loadedMessages.length > 0 ? loadedMessages : [])
    } catch (err) {
      setError(err.message || 'Failed to load conversation')
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const startNewConversation = () => {
    setSelectedConversationId(null)
    setMessages([WELCOME_MESSAGE])
    setError(null)
  }

  const handleSelectConversation = async (conversationId) => {
    setSelectedConversationId(conversationId)
    await loadConversation(conversationId)
  }

  const handleDeleteConversation = async (conversationId) => {
    try {
      await deleteConversation(conversationId)
      setConversations(prev => prev.filter(item => item.id !== conversationId))

      if (selectedConversationId === conversationId) {
        startNewConversation()
      }
    } catch (err) {
      setError(err.message || 'Failed to delete conversation')
    }
  }

  const handleSendMessage = async (text) => {
    const userMessage = {
      id: `user-${Date.now()}`,
      text,
      sender: 'user',
      timestamp: new Date()
    }

    const assistantTempId = `assistant-temp-${Date.now()}`
    setMessages(prev => {
      const draft = prev.filter(message => message.id !== 'intro')
      return [...draft, userMessage, {
        id: assistantTempId,
        text: '',
        sender: 'therapist',
        timestamp: new Date()
      }]
    })
    setIsTyping(true)
    setError(null)

    let assignedConversationId = selectedConversationId
    try {
      await sendMessage(text, selectedConversationId, ({ event, data }) => {
        if (!data) return

        if (!assignedConversationId && data.conversation_id) {
          assignedConversationId = data.conversation_id
          setSelectedConversationId(assignedConversationId)
        }

        if (event === 'message') {
          const chunk = data.assistant_message?.content || data.content || ''
          setMessages(prev => prev.map(message => message.id === assistantTempId
            ? { ...message, text: (message.text || '') + chunk }
            : message))
        } else if (event === 'done') {
          const finalText = typeof data === 'string'
            ? data
            : (data.assistant_message?.content || data.content || '')

          setMessages(prev => prev.map(message => message.id === assistantTempId
            ? { ...message, text: finalText, timestamp: new Date() }
            : message))
          setIsTyping(false)
        }
      })

      await loadConversations()
    } catch (err) {
      setError(err.message || 'Failed to send message')
      setMessages(prev => prev.filter(message => message.id !== userMessage.id && message.id !== assistantTempId))
      setIsTyping(false)
    }
  }

  return (
    <div className="chat-shell">
      <aside className="conversation-sidebar">
        <div className="sidebar-header">
          <h2>Conversations</h2>
          <button className="new-chat-button" onClick={startNewConversation}>+ New</button>
        </div>

        <div className="conversation-list">
          {conversations.length === 0 ? (
            <p className="empty-state">No saved conversations yet.</p>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`conversation-item ${selectedConversationId === conversation.id ? 'selected' : ''}`}
              >
                <button
                  className="conversation-link"
                  type="button"
                  onClick={() => handleSelectConversation(conversation.id)}
                >
                  <span className="conversation-title">{conversation.title || 'New conversation'}</span>
                  <span className="conversation-meta">
                    {new Date(conversation.updated_at).toLocaleDateString()}
                  </span>
                </button>
                <button
                  className="delete-button"
                  type="button"
                  onClick={() => handleDeleteConversation(conversation.id)}
                  aria-label={`Delete conversation ${conversation.title || conversation.id}`}
                >
                  ×
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

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
          {isLoadingHistory && <div className="history-loading">Loading conversation…</div>}
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
    </div>
  )
}

export default ChatInterface
