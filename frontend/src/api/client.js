import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const summarizeEmail = (message) => apiClient.post('/summarize', { message });
export const classifyLead = (message) => apiClient.post('/classify', { message });
export const generateReply = (message, category) => apiClient.post('/generate-reply', { message, category });
export const getAnalytics = () => apiClient.get('/analytics');
export const getLeads = (category = 'all') => apiClient.get(`/leads?category=${category}`);
export const sendFullWorkflowToDiscord = (message) => apiClient.post('/notify/full_workflow', { message });

export const loginUser = (email, password) => apiClient.post('/auth/login', { email, password });
export const registerUser = (name, email, password) => apiClient.post('/auth/register', { name, email, password });

export default apiClient;
