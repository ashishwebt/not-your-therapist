import '../styles/ChatMessage.css'

function ChatMessage({ message }) {
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }

  return (
    <div className={`message ${message.sender}-message`}>
      <div className="message-content">
        <p className="message-text">{message.text}</p>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>
    </div>
  )
}

export default ChatMessage
