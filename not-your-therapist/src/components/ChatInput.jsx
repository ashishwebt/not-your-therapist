import { useState, useRef } from 'react'
import '../styles/ChatInput.css'

function ChatInput({ onSendMessage, disabled = false }) {
  const [input, setInput] = useState('')
  const inputRef = useRef(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSendMessage(input)
      setInput('')
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit} className="chat-input-form">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyUp={handleKeyPress}
          placeholder="Share your thoughts here..."
          className="chat-input"
          rows="1"
          disabled={disabled}
        />
        <button type="submit" className="send-button" disabled={!input.trim() || disabled}>
          <span className="send-icon">→</span>
        </button>
      </form>
      <p className="input-hint">Press Enter to send, Shift+Enter for new line</p>
    </div>
  )
}

export default ChatInput
