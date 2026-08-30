const API_BASE_URL = import.meta.env.VITE_CHAT_SERVICE_URL || 'http://localhost:8000/api/v1';
const CLIENT_ID = '00000000-0000-0000-0000-000000000000'; // Default for now, should be managed via auth

export interface Conversation {
  id: string;
  title: string;
  last_message_at: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  content: string;
  role: 'USER' | 'SYSTEM';
  resources?: any[];
  created_at?: string;
}

export interface ConversationDetail {
  conversation: Conversation;
  messages: Message[];
}

export const chatService = {
  async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${API_BASE_URL}/conversation`, {
      headers: { 'X-Client-ID': CLIENT_ID },
    });
    const result = await response.json();
    return result.data;
  },

  async createConversation(): Promise<Conversation> {
    const response = await fetch(`${API_BASE_URL}/conversation`, {
      method: 'POST',
      headers: { 'X-Client-ID': CLIENT_ID },
    });
    const result = await response.json();
    return result.data;
  },

  async getConversationDetail(id: string): Promise<ConversationDetail> {
    const response = await fetch(`${API_BASE_URL}/conversation/${id}`, {
      headers: { 'X-Client-ID': CLIENT_ID },
    });
    const result = await response.json();
    return result.data;
  },

  async deleteConversation(id: string) {
    await fetch(`${API_BASE_URL}/conversation/${id}`, {
      method: 'DELETE',
      headers: { 'X-Client-ID': CLIENT_ID },
    });
  },

  async updateConversationTitle(id: string, title: string) {
    const response = await fetch(`${API_BASE_URL}/conversation/${id}/title`, {
      method: 'PATCH',
      headers: { 
        'X-Client-ID': CLIENT_ID,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title }),
    });
    return response.json();
  },

  async *streamMessage(conversationId: string, content: string) {
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: { 
        'X-Client-ID': CLIENT_ID,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content }),
    });

    if (!response.body) return;

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      yield chunk;
    }
  }
};
