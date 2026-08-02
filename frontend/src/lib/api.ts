import axios from 'axios';

// In-memory access token storage
let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  accessToken = token;
};

export const getAccessToken = () => accessToken;

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true, // Crucial for sending/receiving HttpOnly cookies
});

// Request interceptor to attach access token if available
api.interceptors.request.use((config) => {
  if (config.headers) {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    config.headers['Cache-Control'] = 'no-cache';
    config.headers['Pragma'] = 'no-cache';
    config.headers['Expires'] = '0';
  }
  return config;
});

// Response interceptor to handle 401s and refresh the token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already retried this request
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Attempt to refresh the token via HttpOnly cookie
        const res = await axios.post(
          'http://localhost:8000/auth/refresh',
          {},
          { withCredentials: true }
        );
        const newAccessToken = res.data.access_token;
        setAccessToken(newAccessToken);
        
        // Update the original request's Authorization header
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, clear token and reject
        setAccessToken(null);
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
