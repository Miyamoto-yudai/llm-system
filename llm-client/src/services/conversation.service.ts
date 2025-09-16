import { api } from './api.config'

export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count?: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ConversationWithMessages {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: Message[]
}

export interface CreateConversationDto {
  title?: string
}

export interface CreateMessageDto {
  role: 'user' | 'assistant'
  content: string
}

export const conversationService = {
  async getConversations(skip = 0, limit = 20): Promise<Conversation[]> {
    const response = await api.get<Conversation[]>('/api/conversations', {
      params: { skip, limit }
    })
    return response.data
  },

  async getConversation(id: string): Promise<ConversationWithMessages> {
    const response = await api.get<ConversationWithMessages>(`/api/conversations/${id}`)
    return response.data
  },

  async createConversation(data: CreateConversationDto = {}): Promise<Conversation> {
    const response = await api.post<Conversation>('/api/conversations', data)
    return response.data
  },

  async updateConversationTitle(id: string, title: string): Promise<void> {
    await api.put(`/api/conversations/${id}`, { title })
  },

  async deleteConversation(id: string): Promise<void> {
    await api.delete(`/api/conversations/${id}`)
  },

  async addMessage(conversationId: string, message: CreateMessageDto): Promise<Message> {
    const response = await api.post<Message>(
      `/api/conversations/${conversationId}/messages`,
      message
    )
    return response.data
  }
}