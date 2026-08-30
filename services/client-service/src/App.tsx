import React, { useRef, useState, useEffect } from "react"
import { Textarea } from "./components/ui/textarea"
import { ScrollArea } from "./components/ui/scroll-area"
import { ArrowUp, LoaderCircle } from "lucide-react"
import clsx from "clsx"
import { Sidebar } from "./components/Sidebar"
import { ChatMessage } from "./components/chat/ChatMessage"
import { chatService, Conversation } from "./services/chat"

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [streamingStatus, setStreamingStatus] = useState<string | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [history, setHistory] = useState<{ messager: string, message: string, resources: any[] }[]>([])
  const [message, setMessage] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { loadConversations() }, [])
  useEffect(() => {
    if (activeId) loadConversationDetail(activeId)
    else setHistory([])
  }, [activeId])

  const loadConversations = async () => {
    try { 
      const data = await chatService.getConversations()
      setConversations(data) 
    } catch (e) {}
  }

  const loadConversationDetail = async (id: string) => {
    try {
      const data = await chatService.getConversationDetail(id)
      setHistory(data.messages.map((m: any) => ({
        messager: m.role === 'AGENT' ? 'SYSTEM' : m.role, 
        message: m.content, 
        resources: m.resources || []
      })))
    } catch (e) {}
  }

  const handleNewChat = async () => {
    try {
      const newConv = await chatService.createConversation()
      setConversations([newConv, ...conversations])
      setActiveId(newConv.id)
    } catch (e) {}
  }

  const handleDeleteChat = async (id: string) => {
    try {
      await chatService.deleteConversation(id)
      setConversations(conversations.filter(c => c.id !== id))
      if (activeId === id) setActiveId(null)
    } catch (e) {}
  }

  const handleSend = async () => {
    if (!message.trim()) return;
    let currentId = activeId;
    if (!currentId) {
      try {
        const newConv = await chatService.createConversation()
        setConversations(prev => [newConv, ...prev]); 
        setActiveId(newConv.id); 
        currentId = newConv.id
      } catch (e) { return }
    }
    const currentMessage = message;
    setIsLoading(true); 
    setHistory(prev => [...prev, { messager: "USER", message: currentMessage, resources: [] }]); 
    setMessage("")

    try {
      let agentMsg = { messager: "SYSTEM", message: "", resources: [] }
      setHistory(prev => [...prev, agentMsg])
      const stream = chatService.streamMessage(currentId!, currentMessage)
      for await (const chunk of stream) {
        chunk.split('\n').forEach(line => {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.status) {
                setStreamingStatus(data.status)
              }
              if (data.answer) {
                setStreamingStatus(null)
                agentMsg.message += data.answer
                setHistory(prev => [...prev.slice(0, -1), { ...agentMsg }])
              }
            } catch (e) {}
          }
        })
      }
    } catch (e) {}
    setIsLoading(false); 
    setStreamingStatus(null);
    loadConversations()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="flex h-screen w-screen bg-neutral-900 text-neutral-50 overflow-hidden">
      <Sidebar conversations={conversations} activeId={activeId} onSelect={setActiveId} onNew={handleNewChat} onDelete={handleDeleteChat} />
      <div className="flex-1 flex flex-col items-center relative overflow-hidden bg-neutral-800">
        <ScrollArea className={clsx("w-full flex justify-center overflow-auto", history.length !== 0 ? "h-[90vh]" : "h-[30vh]")}>
          <div className="max-w-3xl w-[90%] mx-auto flex flex-col gap-4 my-8">
            {history.length === 0 && (
              <div className="text-center mt-20">
                <h1 className="text-4xl font-bold mb-4">How can I help you?</h1>
                <p className="text-neutral-400">Ask anything about the Quran and its teachings.</p>
              </div>
            )}
            {history.map((item, index) => <ChatMessage key={index} item={item} />)}
            {streamingStatus && (
              <div className="flex items-center gap-2 text-sm text-neutral-400 italic animate-pulse ml-4">
                <LoaderCircle className="animate-spin" size={14} />
                {streamingStatus}...
              </div>
            )}
          </div>
        </ScrollArea>
        <div className={clsx("max-w-3xl w-[90%] absolute bottom-8 transition-all", history.length === 0 && "top-1/2 -translate-y-1/2")}>
          <div className="relative bg-neutral-700 rounded-2xl p-2 border border-neutral-600 focus-within:border-neutral-500">
            <Textarea rows={1} placeholder="Ask anything..." className="w-full bg-transparent border-none focus-visible:ring-0 resize-none py-3 px-4 max-h-[200px]" value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={handleKeyDown} />
            <div className="flex justify-end p-1">
              <button disabled={isLoading || !message.trim()} onClick={handleSend} className="bg-white text-black p-2 rounded-xl disabled:opacity-50 hover:bg-neutral-200">
                {isLoading ? <LoaderCircle className="animate-spin" size={20} /> : <ArrowUp size={20} />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
export default App
