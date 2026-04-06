<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title" style="color: black !important;">Iniciar Sesión</h2>
      <p class="subtitle" style="color: #666 !important;">Bienvenido de nuevo a Fori</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="form-group">
          <label for="email" style="color: black !important;">Correo Electrónico</label>
          <input
            type="email"
            id="email"
            v-model="form.email"
            placeholder="Introduce tu correo"
            required
            :disabled="isLoading"
            class="input-field"
            style="color: black !important; background-color: white !important;"
          />
        </div>

        <div class="form-group">
          <label for="password" style="color: black !important;">Contraseña</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            placeholder="Introduce tu contraseña"
            required
            :disabled="isLoading"
            class="input-field"
            style="color: black !important; background-color: white !important;"
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loader"></span>
          <span v-else>Ingresar</span>
        </button>
      </form>

      <div class="redirect-container" style="color: black !important; margin-bottom: 8px;">
        <router-link to="/recovery" class="redirect-link" style="color: #4a90e2 !important;">¿Olvidaste tu contraseña?</router-link>
      </div>
      <div class="redirect-container" style="color: black !important; margin-top: 8px;">
        ¿No tienes una cuenta?
        <router-link to="/register" class="redirect-link" style="color: #4a90e2 !important;">Regístrate aquí</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const isLoading = ref(false);
const errorMessage = ref('');

const form = reactive({
  email: '',
  password: ''
});

const handleLogin = async () => {
  errorMessage.value = '';
  isLoading.value = true;

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // FastApi espera un objeto JSON literal (no form-urlencoded) basado en UserLogin de FastAPI
      body: JSON.stringify({
        email: form.email,
        password: form.password
      })
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 400 || response.status === 404) {
          errorMessage.value = 'Correo electrónico o contraseña incorrectos.';
      } else {
          errorMessage.value = 'Error del servidor. Por favor, inténtalo más tarde.';
      }
      return;
    }

    const data = await response.json();

    if (data.mfa_required) {
      // Guardar temp_token para el segundo paso (MFA)
      authStore.setTempToken(data.temp_token);
      router.push('/mfa');
      return;
    }

    // Flujo normal sin MFA: Guardamos en el Store global
    authStore.setAccessToken(data.access_token || data.token);
    
    // Retrocompatibilidad con localStorage explícito del proyecto
    localStorage.setItem('token', data.access_token || data.token);

    // El backend no devuelve objeto 'user', lo construimos con el email del form
    const userToSave = data.user || { email: form.email };
    authStore.setUser(userToSave);

    window.location.href = '/perfil';
    
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorMessage.value = 'No se pudo conectar con el servidor. ¿Está encendido?';
    } else {
      errorMessage.value = 'Ocurrió un error inesperado al iniciar sesión.';
    }
    console.error('Error in login:', error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  font-size: 14px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.input-field:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.error-message {
  background-color: #fee2e2;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  text-align: center;
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #4a90e2, #357abd);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 48px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(74, 144, 226, 0.3);
}

.submit-btn:disabled {
  background: #a0c4eb;
  cursor: not-allowed;
}

.loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.redirect-container {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
}

.redirect-link {
  font-weight: 600;
  text-decoration: none;
  transition: color 0.3s ease;
}

.redirect-link:hover {
  text-decoration: underline;
}
</style>