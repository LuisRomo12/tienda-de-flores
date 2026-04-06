<template>
  <div class="mfa-page">
    <div class="mfa-card">
      <div class="mfa-header">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon-lock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
        <h2>Seguridad de la Cuenta</h2>
        <p class="subtitle">Protege tu cuenta con autenticación de dos factores</p>
      </div>
      
      <!-- Paso 1: Configurar (Solo si es nuevo usuario configurándolo) -->
      <div v-if="isSettingUp" class="mfa-setup">
        <p class="setup-instruction">Escanea el código QR en tu App Autenticadora:</p>
        <div class="qr-container">
          <qrcode-vue v-if="qrUrl" :value="qrUrl" :size="200" level="M" />
        </div>
        
        <div class="manual-key-container">
          <label>O ingresa tu llave manual:</label>
          <div class="input-with-copy">
            <input type="text" readonly :value="secret" />
            <button @click="copySecret" type="button" class="copy-btn" title="Copiar llave">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Paso 2: Verificar -->
      <div class="mfa-verify">
        <p class="verify-instruction">Selecciona el método de verificación:</p>
        
        <div class="method-selector">
          <label class="method-pill" :class="{ active: selectedMethod === 'totp' }">
            <input type="radio" value="totp" v-model="selectedMethod"> 
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect>
              <line x1="12" y1="18" x2="12.01" y2="18"></line>
            </svg>
            App Autenticadora
          </label>
          <label class="method-pill" :class="{ active: selectedMethod === 'email' }">
            <input type="radio" value="email" v-model="selectedMethod" @change="requestEmailOTP"> 
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            Email
          </label>
        </div>

        <transition name="fade">
          <div v-if="message" class="notification-banner" :class="messageType">
            {{ message }}
          </div>
        </transition>

        <div class="code-input-container">
          <input 
            type="text" 
            v-model="verificationCode" 
            maxlength="6" 
            placeholder="000000"
            class="code-input"
            @keyup.enter="submitVerification"
          />
        </div>
        
        <button class="btn-primary" @click="submitVerification" :disabled="!verificationCode || verificationCode.length < 6">
          Aceptar Código
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import QrcodeVue from 'qrcode.vue';
import apiClient from '@/api/axios';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const isSettingUp = ref(false);
const qrUrl = ref('');
const secret = ref('');
const verificationCode = ref('');
const selectedMethod = ref('totp'); // 'totp' o 'email'
const message = ref('');
const messageType = ref(''); // 'success' o 'error'

const authStore = useAuthStore();
const router = useRouter();

// Mostrar mensajes con un tipo definido para el estilo (success/error)
const showMessage = (msg, type = 'success') => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    // Solo limpiar si no hay un nuevo mensaje pendiente
    if (message.value === msg) {
      message.value = '';
    }
  }, 5000);
};

// Copiar al portapapeles
const copySecret = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(secret.value);
      showMessage('¡Llave copiada al portapapeles!', 'success');
    } else {
      // Fallback
      const textArea = document.createElement("textarea");
      textArea.value = secret.value;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      showMessage('¡Llave copiada al portapapeles!', 'success');
    }
  } catch (err) {
    console.error('Error al copiar: ', err);
    showMessage('Error al copiar la llave', 'error');
  }
};

// Función Opcional: Solicitar QR si el usuario no tiene MFA aún
async function fetchMfaSetup() {
  try {
    const { data } = await apiClient.post('/api/auth/mfa/setup-totp');
    qrUrl.value = data.qr_code_url;
    secret.value = data.secret;
    isSettingUp.value = true;
  } catch (error) {
    console.error("Error al cargar configuración", error);
    showMessage('Error al cargar la configuración MFA', 'error');
  }
}

async function requestEmailOTP() {
  if (selectedMethod.value === 'email') {
    try {
      const { data } = await apiClient.post('/api/auth/mfa/send-email-otp', {}, {
        headers: { Authorization: `Bearer ${authStore.state.tempToken}` }
      });
      showMessage(data.message, 'success');
    } catch (error) {
      showMessage("Error enviando correo.", 'error');
    }
  }
}

async function submitVerification() {
  if (!verificationCode.value || verificationCode.value.length < 6) return;
  
  try {
    const payload = {
      code: verificationCode.value,
      method: selectedMethod.value
    };

    const { data } = await apiClient.post('/api/auth/verify-mfa', payload, {
      headers: { Authorization: `Bearer ${authStore.state.tempToken}` }
    });

    if (data.mfa_verified && data.access_token) {
      authStore.finalizeLogin(data.access_token);
      showMessage("¡Bienvenido!", 'success');
      setTimeout(() => {
        router.push('/'); // Regresar a home/dashboard
      }, 1000);
    }
  } catch (error) {
    showMessage(error.response?.data?.detail || "Código incorrecto y/o expirado.", 'error');
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

.mfa-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #faf7f5;
  font-family: 'Inter', sans-serif;
  padding: 20px;
}

.mfa-card {
  background: white;
  max-width: 480px;
  width: 100%;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.mfa-header {
  text-align: center;
  margin-bottom: 10px;
}

.icon-lock {
  width: 48px;
  height: 48px;
  color: #c08497;
  margin-bottom: 16px;
  stroke-width: 1.5;
}

.mfa-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 28px;
  color: #333;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.mfa-header .subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.mfa-setup {
  background: #fdfbfb;
  border: 1px solid #f0e6e8;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}

.setup-instruction {
  font-size: 14px;
  color: #555;
  margin-bottom: 16px;
  font-weight: 500;
}

.qr-container {
  background: white;
  padding: 16px;
  border-radius: 12px;
  display: inline-block;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
}

.manual-key-container {
  text-align: left;
}

.manual-key-container label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.input-with-copy {
  display: flex;
  background: white;
  border: 1px solid #e2d5d8;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease;
}

.input-with-copy:focus-within {
  border-color: #c08497;
}

.input-with-copy input {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: #333;
  font-family: monospace;
  font-size: 14px;
  letter-spacing: 1px;
  outline: none;
}

.copy-btn {
  background: #fcf7f8;
  border: none;
  border-left: 1px solid #e2d5d8;
  color: #c08497;
  padding: 0 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.copy-btn:hover {
  background: #f5eef0;
}

.mfa-verify {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.verify-instruction {
  text-align: center;
  font-size: 14px;
  color: #555;
  font-weight: 500;
  margin: 0;
}

.method-selector {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.method-pill {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 1px solid #e2d5d8;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.3s ease;
  background: white;
}

.method-pill input[type="radio"] {
  display: none;
}

.method-pill:hover {
  background: #fcf7f8;
}

.method-pill.active {
  border-color: #c08497;
  background: #fdfbfb;
  color: #c08497;
  box-shadow: 0 2px 8px rgba(192, 132, 151, 0.15);
}

.code-input-container {
  display: flex;
  justify-content: center;
  min-height: 60px; /* Prevenir salto visual */
}

.code-input {
  width: 100%;
  max-width: 240px;
  padding: 16px;
  font-size: 32px;
  letter-spacing: 12px;
  text-align: center;
  border: 2px solid #e2d5d8;
  border-radius: 12px;
  outline: none;
  transition: all 0.3s ease;
  color: #333;
  background: #faf7f5;
}

.code-input:focus {
  border-color: #c08497;
  background: white;
  box-shadow: 0 0 0 4px rgba(192, 132, 151, 0.1);
}

.code-input::placeholder {
  color: #ccc;
}

.btn-primary {
  width: 100%;
  padding: 16px;
  background-color: #c08497;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Inter', sans-serif;
  margin-top: 10px;
}

.btn-primary:hover:not(:disabled) {
  background-color: #ab7184;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(192, 132, 151, 0.3);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  background-color: #e2d5d8;
  cursor: not-allowed;
  opacity: 0.7;
}

.notification-banner {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  font-weight: 500;
}

.notification-banner.success {
  background-color: #e6f4ea;
  color: #1e4620;
  border: 1px solid #ceead6;
}

.notification-banner.error {
  background-color: #fce8e6;
  color: #a50e0e;
  border: 1px solid #fad2cf;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 480px) {
  .mfa-card {
    padding: 24px;
  }
  
  .method-selector {
    flex-direction: column;
  }
  
  .code-input {
    font-size: 24px;
    letter-spacing: 8px;
  }
}
</style>
