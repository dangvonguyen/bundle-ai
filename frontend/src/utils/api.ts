import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  sendMessage: async (chatId: string | null, message: string) => {
    const response = await api.post('/chat', {
      conversation_id: chatId,
      message,
    });
    return response.data;
  },

  getChat: async (chatId: string) => {
    const response = await api.get(`/chat/${chatId}`);
    return response.data;
  },

  deleteChat: async (chatId: string) => {
    const response = await api.delete(`/chat/${chatId}`);
    return response.data;
  },
};

export default api;
