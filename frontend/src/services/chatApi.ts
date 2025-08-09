import axios from 'axios';
import { ChatResponse } from '@/types/chat';

const API_BASE_URL = 'http://localhost:8000';

export const chatApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: message
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000, // 30 second timeout
      });
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
          throw new Error('Unable to connect to the AI service. Please make sure the backend is running on localhost:8000.');
        }
        if (error.response?.status === 404) {
          throw new Error('Chat endpoint not found. Please check the API configuration.');
        }
        if (error.response?.status >= 500) {
          throw new Error('AI service is temporarily unavailable. Please try again.');
        }
        throw new Error(error.response?.data?.message || 'Failed to send message. Please try again.');
      }
      throw new Error('An unexpected error occurred. Please try again.');
    }
  }
};