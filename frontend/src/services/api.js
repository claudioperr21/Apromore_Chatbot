import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for chart generation
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.error || error.response.data?.message || 'Server error';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      // Something else happened
      throw new Error(error.message || 'Network error');
    }
  }
);

// API functions for main.py integration
export const fetchChat = async (dataset, message) => {
  const response = await api.post('/chat', {
    dataset: dataset,
    message: message
  });
  return response;
};

export const fetchAnalysis = async (dataset, query) => {
  const response = await api.post(`/analyze/${dataset}`, {
    query: query
  });
  return response;
};

export const fetchChart = async (dataset, chartType) => {
  const response = await api.get(`/chart/${dataset}/${chartType}`);
  return response;
};

export const exportPDF = async (dataset, chartTypes, title) => {
  const response = await api.post('/export/pdf', {
    dataset: dataset,
    chart_types: chartTypes,
    title: title
  }, {
    responseType: 'blob' // Important for file downloads
  });
  return response;
};

export const exportChatHistory = async (chatHistory) => {
  const response = await api.post('/export/chat', {
    chat_history: chatHistory
  });
  return response;
};

export const switchDataset = async (dataset) => {
  const response = await api.post('/switch', {
    dataset: dataset
  });
  return response;
};

export const getSystemStatus = async () => {
  const response = await api.get('/status');
  return response;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response;
};

export default api;
