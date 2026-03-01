const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function sendMessage(message, conversationId = null, onChunk = null) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message: message,
    }),
  })

  if (!response.ok) {
    // Try to parse JSON error body
    let errMsg = 'Failed to send message'
    try {
      const error = await response.json()
      errMsg = error.detail || errMsg
    } catch (e) {}
    throw new Error(errMsg)
  }

  const convId = response.headers.get('X-Conversation-Id') || null

  // If caller doesn't want streaming chunks, fall back to returning full JSON
  if (!response.body) {
    const json = await response.json()
    return { conversation_id: convId, data: json }
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  const processEvent = (raw) => {
    const lines = raw.split('\n').filter(Boolean)
    let event = 'message'
    const dataLines = []
    for (const line of lines) {
      if (line.startsWith('event:')) {
        event = line.replace('event:', '').trim()
      } else if (line.startsWith('data:')) {
        dataLines.push(line.replace('data:', '').trim())
      }
    }
    const dataStr = dataLines.join('\n')
    let parsed = dataStr
    try {
      parsed = JSON.parse(dataStr)
    } catch (e) {}
    if (onChunk) onChunk({ event, data: parsed })
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop()
    for (const part of parts) {
      processEvent(part)
    }
  }

  if (buffer.trim()) {
    processEvent(buffer)
  }

  return { conversation_id: convId }
}

export async function getConversations() {
  const response = await fetch(`${API_BASE_URL}/conversations`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch conversations')
  }

  return await response.json()
}

export async function getConversation(conversationId) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch conversation')
  }

  return await response.json()
}

export async function deleteConversation(conversationId) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Failed to delete conversation')
  }

  return await response.json()
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Backend health check failed')
  }

  return await response.json()
}
