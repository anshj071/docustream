import axios from 'axios';

const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
const apiBase = configuredApiUrl
  ? `${configuredApiUrl.replace(/\/+$/, '')}/api/v1`
  : process.env.NODE_ENV === 'development'
    ? '/api/v1'
    : (() => { throw new Error('NEXT_PUBLIC_API_URL must be set to the Render backend URL in Vercel.'); })();

const api = axios.create({
  baseURL: apiBase,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
