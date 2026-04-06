import { reactive, readonly } from 'vue';

const state = reactive({
  tempToken: null,
  accessToken: localStorage.getItem('access_token') || localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
});

const setTempToken = (token) => {
  state.tempToken = token;
};

const finalizeLogin = (finalToken) => {
  state.tempToken = null;
  setAccessToken(finalToken);
  // Guardado explícito como se solicitó, además de retrocompatibilidad
  localStorage.setItem('access_token', finalToken);
  localStorage.setItem('token', finalToken);
};

const setAccessToken = (token) => {
  state.accessToken = token;
  if (token) {
    localStorage.setItem('access_token', token);
    localStorage.setItem('token', token);
  } else {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token');
  }
};

const setUser = (userData) => {
  state.user = userData;
  if (userData) {
    localStorage.setItem('user', JSON.stringify(userData));
  } else {
    localStorage.removeItem('user');
  }
};

const logout = () => {
  setAccessToken(null);
  setUser(null);
  // Eliminamos el valor the refresh_token cookie automatically inside axios if we call an endpoint, 
  // but here we just clear local state.
};

export const useAuthStore = () => ({
  state: readonly(state),
  setTempToken,
  finalizeLogin,
  setAccessToken,
  setUser,
  logout
});
