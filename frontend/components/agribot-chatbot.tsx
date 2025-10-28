"use client"

import { useState, useRef, useEffect } from "react"
import { Send, MessageCircle, X } from "lucide-react"

interface Message {
  id: string
  text: string
  sender: "user" | "bot"
  timestamp: Date
}

const botResponses: { [key: string]: string } = {
  hello: "Hello! I'm AgriBot, your agricultural assistant. How can I help you today?",
  price: "Current market prices vary by product and location. Check our marketplace for real-time pricing!",
  listing:
    "To create a listing, go to your dashboard and click 'Create New Listing'. Upload photos, set your price, and we'll help optimize it!",
  payment:
    "We support M-Pesa, bank transfers, and digital wallets. Payments are secured in escrow until delivery confirmation.",
  blockchain:
    "Our blockchain system records every transaction immutably, creating a permanent record of your business history.",
  help: "I can help with: pricing, listings, payments, blockchain info, and general questions. What would you like to know?",
  default: "That's a great question! For more detailed help, please contact our support team or visit our help center.",
}

export default function AgribotChatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Hello! I'm AgriBot. How can I assist you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")

    // Simulate bot response
    setTimeout(() => {
      const lowerInput = inputValue.toLowerCase()
      let botResponse = botResponses.default

      for (const [key, response] of Object.entries(botResponses)) {
        if (lowerInput.includes(key)) {
          botResponse = response
          break
        }
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponse,
        sender: "bot",
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, botMessage])
    }, 500)
  }

  return (
    <>
      {/* Chatbot Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-primary hover:bg-primary-dark text-white rounded-full p-4 shadow-lg transition-smooth z-40"
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chatbot Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 max-w-[calc(100vw-24px)] bg-white rounded-xl shadow-2xl border border-border flex flex-col z-40 h-96">
          {/* Header */}
          <div className="bg-primary text-white p-4 rounded-t-xl">
            <h3 className="font-bold text-lg">AgriBot Assistant</h3>
            <p className="text-sm text-white/80">Always here to help</p>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    message.sender === "user"
                      ? "bg-primary text-white rounded-br-none"
                      : "bg-background-secondary text-foreground rounded-bl-none"
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-border p-4 flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            <button
              onClick={handleSendMessage}
              className="bg-primary hover:bg-primary-dark text-white p-2 rounded-lg transition-smooth"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
