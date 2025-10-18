import React, { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Bot, User, Lightbulb } from 'lucide-react'

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
  suggestions?: string[]
  isThought?: boolean
}

interface ChatResponse {
  response: string
  timestamp: string
  suggestions: string[]
}

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'How can I help you?',
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Subscribe to backend WebSocket for MCP tool telemetry
  useEffect(() => {
    const clientId = `ui-${Math.random().toString(36).slice(2, 8)}`
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${clientId}`)
    wsRef.current = ws
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        const isTelemetry = ['llm_router(mcp)','mcp_trace','mcp_tool'].includes(msg?.type)
        if (isTelemetry) {
          const data = msg.data || {}
          const stage = (data.stage || '').toString().toLowerCase()
          let line = ''
          if (msg.type === 'llm_router(mcp)' && stage === 'start') {
            const model = (data.args && data.args.model) || 'unknown'
            line = `[LLM] model=${model}`
          } else if (msg.type === 'llm_router(mcp)' && stage === 'end') {
            // Summarize router decision as a plan line
            let tool = 'unknown'
            let params: any = {}
            try {
              const summary = data.resultSummary || ''
              const parsed = typeof summary === 'string' ? JSON.parse(summary) : summary
              if (parsed && typeof parsed === 'object') {
                tool = parsed.tool_name || tool
                params = parsed.parameters || {}
              }
            } catch {}
            line = `[PLAN] tool=${tool} params=${JSON.stringify(params)}`
          } else if (msg.type === 'mcp_trace' && stage === 'start') {
            const tool = data.tool || 'tool'
            const params = data.params || {}
            line = `[TOOL] ${tool} params=${JSON.stringify(params)}`
          } else if (msg.type === 'mcp_trace' && stage === 'end') {
            const tool = data.tool || 'tool'
            const summary = data.resultSummary || 'ok'
            line = `[RESULT] ${tool} → ${summary}`
          } else if (msg.type === 'mcp_tool') {
            const tool = data.tool || 'tool'
            if (stage === 'start') {
              const args = data.args || {}
              line = `[TOOL] ${tool} params=${JSON.stringify(args)}`
            } else if (stage === 'end') {
              const summary = data.resultSummary || 'ok'
              line = `[RESULT] ${tool} → ${summary}`
            } else if (stage === 'error') {
              const reason = (data.args && data.args.reason) || (data.args && data.args.error) || 'error'
              line = `[RESULT] ${tool} → error (${reason})`
            } else {
              return
            }
          } else {
            // ignore other lines (e.g., llm_router end)
            return
          }

          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            if (!last || last.isUser !== false || !last.isThought) {
              next.push({ id: `${Date.now()}-${Math.random()}`, text: line, isUser: false, isThought: true, timestamp: new Date() })
            } else {
              next[next.length - 1] = { ...last, text: `${last.text}\n${line}` }
            }
            return next
          })
        }
      } catch {
        // ignore non-JSON messages
      }
    }
    ws.onclose = () => {
      wsRef.current = null
    }
    return () => {
      try { ws.close() } catch {}
    }
  }, [])

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/ai/intelligent-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text.trim(),
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response from AI')
      }

      const data: ChatResponse = await response.json()

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(data.timestamp),
        suggestions: data.suggestions
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Chatbot error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        isUser: false,
        timestamp: new Date(),
        suggestions: ["Try again", "Check connection"]
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputText)
  }

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion)
  }

  const toggleChatbot = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div className="fixed bottom-4 right-4 z-[9999] chatbot-container">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-[22rem] md:w-[28rem] h-[calc(100vh-2rem)] bg-white/95 backdrop-blur rounded-2xl shadow-2xl border border-gray-200/60 flex flex-col overflow-hidden animate-in slide-in-from-bottom-2 duration-300">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 rounded-t-2xl flex items-center justify-between shadow">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Bot className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 inline-block w-2 h-2 bg-emerald-400 rounded-full ring-2 ring-white"></span>
              </div>
              <div>
                <h3 className="font-semibold text-sm leading-tight">ResQMap AI</h3>
                <p className="text-xs opacity-90">Disaster Intelligence Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={toggleChatbot}
                className="text-white/90 hover:text-white transition-colors p-1.5 rounded-md hover:bg-white/20"
                aria-label="Close chatbot"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>


          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-white to-gray-50">
            {messages.map((message) => (
              <div key={message.id} className="space-y-2">
                <div
                  className={`flex ${
                    message.isUser ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`${message.isThought ? 'max-w-[95%]' : 'max-w-[85%]'} p-3 rounded-2xl text-sm shadow-sm ring-1 ring-black/5 break-words ${
                      message.isThought
                        ? 'bg-yellow-50 text-yellow-900 border border-yellow-200'
                        : message.isUser
                        ? 'bg-blue-600 text-white rounded-br-2xl ring-0 shadow'
                        : 'bg-white text-gray-800 rounded-bl-2xl border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {!message.isUser && !message.isThought && (
                        <Bot className="w-4 h-4 mt-0.5 flex-shrink-0 text-blue-600" />
                      )}
                      {!message.isUser && message.isThought && (
                        <Lightbulb className="w-4 h-4 mt-0.5 flex-shrink-0 text-yellow-600" />
                      )}
                      {message.isUser && (
                        <User className="w-4 h-4 mt-0.5 flex-shrink-0 text-white/90" />
                      )}
                      <div className="flex-1 min-w-0">
                        {message.isThought ? (
                          <div className="space-y-1 font-mono text-[12px] whitespace-pre-wrap break-words overflow-x-hidden">
                            {message.text.split('\n').map((line, idx) => {
                              const m = line.match(/^\[(LLM|PLAN|TOOL|RESULT)\]\s*(.*)$/)
                              if (m) {
                                const tag = m[1]
                                const rest = m[2]
                                const tagClass = tag === 'LLM'
                                  ? 'bg-indigo-100 text-indigo-700 border-indigo-200'
                                  : tag === 'PLAN'
                                  ? 'bg-purple-100 text-purple-700 border-purple-200'
                                  : tag === 'TOOL'
                                  ? 'bg-amber-100 text-amber-800 border-amber-200'
                                  : 'bg-emerald-100 text-emerald-700 border-emerald-200'
                                const restClass = tag === 'TOOL'
                                  ? 'leading-snug whitespace-nowrap overflow-hidden text-ellipsis max-w-full'
                                  : 'leading-snug break-words max-w-full'
                                return (
                                  <div key={idx} className="flex items-start gap-2 max-w-full min-w-0">
                                    <span className={`inline-flex items-center px-1.5 py-0.5 rounded border text-[10px] leading-none ${tagClass}`}>{tag}</span>
                                    <span className={`${restClass} block min-w-0`} title={rest}>{rest}</span>
                                  </div>
                                )
                              }
                              return (
                                <div key={idx} className="leading-snug break-words max-w-full">{line}</div>
                              )
                            })}
                          </div>
                        ) : (
                          <p className={`leading-relaxed`}>{message.text}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Suggestions */}
                {!message.isUser && message.suggestions && message.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 ml-6">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="text-xs bg-blue-50/80 hover:bg-blue-100 text-blue-700 px-3 py-1.5 rounded-full border border-blue-100 shadow-sm transition-colors flex items-center space-x-1"
                        disabled={isLoading}
                      >
                        <Lightbulb className="w-3 h-3" />
                        <span>{suggestion}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 p-3 rounded-2xl rounded-bl-2xl border border-gray-200 max-w-[70%] shadow-sm">
                  <div className="flex items-center space-x-2">
                    <Bot className="w-4 h-4 text-blue-600" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-3 md:p-4 bg-white/90">
            <form onSubmit={handleSubmit} className="flex space-x-2 items-center">
              <input
                ref={inputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Ask about weather, disasters, maps..."
                className="flex-1 border border-gray-300 rounded-full px-4 py-2.5 text-sm bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/60 focus:border-transparent shadow-sm"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputText.trim() || isLoading}
                className="bg-blue-600 text-white p-2.5 rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                aria-label="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Chat Button - Only show when chatbot is closed */}
      {!isOpen && (
        <button
          onClick={toggleChatbot}
          className="w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
          style={{ border: 'none', outline: 'none' }}
        >
          <MessageCircle className="w-6 h-6 text-white" />
        </button>
      )}

    </div>
  )
}

export default Chatbot
