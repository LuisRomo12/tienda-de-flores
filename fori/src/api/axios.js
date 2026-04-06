import axios from 'axios';
import { useAuthStore } from '../stores/auth.js';
// Replace this with standard router import from your app
import router from '../router/index.js';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  // Permite el envío de cookies HttpOnly
  withCredentials: true, 
});

apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.state.accessToken;
    
    // Solo inyectar el token si no existe ya un header Authorization definido manualmente
    // (Por ejemplo, MFA usa authStore.state.tempToken y lo pasa directo)
    if (token && !config.headers['Authorization'] && !config.headers.Authorization) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // Ignorar si el endpoint era refresh o login para evitar ciclos
      if (originalRequest.url.includes('/refresh') || originalRequest.url.includes('/login')) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;
      const authStore = useAuthStore();

      try {
        const { data } = await axios.post('/api/auth/refresh', {}, {
          baseURL: apiClient.defaults.baseURL,
          withCredentials: true 
        });

        const newAccessToken = data.access_token;
        authStore.setAccessToken(newAccessToken);

        processQueue(null, newAccessToken);
        
        originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
        return apiClient(originalRequest);
      } catch (err) {
        processQueue(err, null);
        authStore.logout();
        alert("Su sesión ha expirado. Por favor, inicie sesión nuevamente.");
        router.push('/login');
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
