<template>
  <div class="recovery-container">
    <div class="recovery-card">
      <h2 class="recovery-title">Recuperación de Contraseña</h2>
      
      <!-- STEP 1: Email Input -->
      <div v-if="step === 1" class="step fade-in">
        <p>Ingresa tu correo electrónico para comenzar.</p>
        <div class="form-group">
          <input type="email" v-model="email" placeholder="tu@correo.com" class="input-field" />
        </div>
        <button @click="verifyEmail" class="action-btn" :disabled="!email">Continuar</button>
        <button @click="goToLogin" class="method-btn fade-btn">Volver al inicio de sesión</button>
      </div>

      <!-- STEP 2: Method Selection -->
      <div v-if="step === 2" class="step fade-in">
        <p>Selecciona un método de recuperación:</p>
        <div class="method-list">
          <button @click="selectMethod('email')" class="method-btn">Enviar enlace por Correo</button>
          <button @click="selectMethod('question')" class="method-btn">Pregunta Secreta</button>
          <button @click="selectMethod('sms')" class="method-btn">Mensaje SMS (Simulado)</button>
          <button @click="selectMethod('voice')" class="method-btn">Llamada de Voz (Simulada)</button>
        </div>
        <button @click="step = 1" class="method-btn fade-btn" style="margin-top: 1rem;">Cambiar correo</button>
      </div>

      <!-- STEP 3: Verification Execution -->
      <div v-if="step === 3" class="step fade-in">
        <!-- Email sending visual-->
        <div v-if="method === 'email'">
           <p>Enviando instrucciones por correo...</p>
           <p class="success-msg" v-if="message">{{ message }}</p>
           <button v-if="message" @click="goToLogin" class="action-btn">Terminar</button>
        </div>

        <!-- Secret Question -->
        <div v-if="method === 'question'">
           <p>Responde a tu pregunta de seguridad:</p>
           <p class="question-text"><strong>{{ question }}</strong></p>
           <div class="form-group">
             <input type="text" v-model="answer" placeholder="Tu respuesta..." class="input-field"/>
           </div>
           <p v-if="error" class="error-msg">{{ error }}</p>
           <button @click="verifyQuestion" class="action-btn" :disabled="!answer">Verificar Módulo Experto</button>
        </div>

        <!-- SMS / Voice -->
        <div v-if="method === 'sms' || method === 'voice'">
           <p>Hemos enviado un código de 6 dígitos vía {{ method === 'sms' ? 'SMS' : 'Voz' }}.</p>
           <div class="form-group">
             <input type="text" v-model="otpCode" placeholder="000000" class="input-field" maxlength="6" />
           </div>
           <p v-if="error" class="error-msg">{{ error }}</p>
           <button @click="verifyOTP" class="action-btn" :disabled="otpCode.length < 6">Verificar OTP</button>
        </div>

        <button v-if="!message" @click="step = 2" class="method-btn fade-btn" style="margin-top: 1rem;">Intentar otro método</button>
      </div>

      <!-- STEP 4: Reset Password -->
      <div v-if="step === 4" class="step fade-in">
        <p>Verificado. Crea tu nueva contraseña.</p>
        <div class="form-group">
          <input type="password" v-model="newPassword" placeholder="Nueva Contraseña" class="input-field" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <p v-if="message" class="success-msg">{{ message }}</p>
        <button v-if="!message" @click="resetPassword" class="action-btn" :disabled="newPassword.length < 4">Cambiar Contraseña</button>
        <button v-if="message" @click="goToLogin" class="action-btn">Ir al Login</button>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient from '@/api/axios';

export default {
  name: 'Recovery',
  setup() {
    const router = useRouter();
    const route = useRoute();
    
    const step = ref(1);
    const email = ref('');
    const method = ref('');
    const question = ref('');
    const answer = ref('');
    const otpCode = ref('');
    const newPassword = ref('');
    
    const error = ref('');
    const message = ref('');
    const recoveryToken = ref('');

    onMounted(() => {
      if (route.query.token && route.query.email) {
        email.value = route.query.email;
        recoveryToken.value = route.query.token;
        step.value = 4;
      }
    });

    const verifyEmail = async () => {
      error.value = '';
      if (email.value) step.value = 2;
    };

    const selectMethod = async (selected) => {
      method.value = selected;
      error.value = '';
      message.value = '';
      step.value = 3;

      if (selected === 'email') {
        try {
          const res = await apiClient.post('/api/auth/recovery/email', { email: email.value });
          message.value = res.data.message;
        } catch (err) {
          error.value = "Error enviando correo.";
        }
      } else if (selected === 'question') {
        try {
          const res = await apiClient.get(`/api/auth/recovery/question/${email.value}`);
          question.value = res.data.pregunta;
        } catch (err) {
          error.value = err.response?.data?.detail || "No se pudo obtener la pregunta.";
          step.value = 2;
          alert(error.value);
        }
      } else if (selected === 'sms' || selected === 'voice') {
        try {
          await apiClient.post('/api/auth/recovery/otp/request', { email: email.value, method: selected });
          message.value = "Código enviado a su teléfono simulado en consola.";
        } catch (err) {
          error.value = "Error solicitando código.";
        }
      }
    };

    const verifyQuestion = async () => {
      error.value = '';
      try {
        const res = await apiClient.post('/api/auth/recovery/question/verify', { email: email.value, respuesta: answer.value });
        recoveryToken.value = res.data.token;
        step.value = 4;
      } catch (err) {
        error.value = err.response?.data?.detail || "Respuesta incorrecta.";
      }
    };

    const verifyOTP = async () => {
      error.value = '';
      try {
        const res = await apiClient.post('/api/auth/recovery/otp/verify', { email: email.value, code: otpCode.value });
        recoveryToken.value = res.data.token;
        step.value = 4;
      } catch (err) {
        error.value = err.response?.data?.detail || "Código incorrecto.";
      }
    };

    const resetPassword = async () => {
      error.value = '';
      try {
        const res = await apiClient.post('/api/auth/recovery/reset', {
          email: email.value,
          token: recoveryToken.value,
          new_password: newPassword.value
        });
        message.value = res.data.message;
      } catch (err) {
        error.value = err.response?.data?.detail || "Error actualizando la contraseña.";
      }
    };

    const goToLogin = () => {
      router.push('/login');
    };

    return {
      step, email, method, question, answer, otpCode, newPassword, error, message,
      verifyEmail, selectMethod, verifyQuestion, verifyOTP, resetPassword, goToLogin
    };
  }
}
</script>

<style scoped>
.recovery-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: transparent;
}
.recovery-card {
  background: #1c1c1c;
  padding: 2.5rem;
  border-radius: 12px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  border: 1px solid #333;
  color: #fff;
  font-family: 'Inter', sans-serif;
}
.recovery-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #e0e0e0;
}
.step p {
  margin-bottom: 1rem;
  font-size: 0.95rem;
  color: #bbb;
  text-align: center;
}
.form-group {
  margin-bottom: 1.5rem;
}
.input-field {
  width: 100%;
  padding: 12px;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  color: #fff;
  font-size: 1rem;
  transition: border-color 0.2s;
}
.input-field:focus {
  outline: none;
  border-color: #7d5a5a;
}
.action-btn {
  width: 100%;
  padding: 12px;
  background: #7d5a5a;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
  margin-bottom: 0.8rem;
}
.action-btn:disabled {
  background: #3a3a3a;
  color: #888;
  cursor: not-allowed;
}
.action-btn:hover:not(:disabled) {
  background: #9c7272;
}
.method-btn {
  width: 100%;
  padding: 12px;
  background: #2a2a2a;
  color: #e0e0e0;
  border: 1px solid #444;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 0.8rem;
}
.method-btn:hover {
  background: #333;
  border-color: #7d5a5a;
}
.fade-btn {
  background: transparent;
  border: none;
  color: #888;
}
.fade-btn:hover {
  color: #e0e0e0;
  background: transparent;
  text-decoration: underline;
}
.method-list {
  display: flex;
  flex-direction: column;
}
.error-msg {
  color: #ff6b6b;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 1rem;
}
.success-msg {
  color: #51cf66;
  font-size: 0.95rem;
  text-align: center;
  margin-bottom: 1rem;
}
.question-text {
  font-size: 1.1rem;
  color: #fff;
  text-align: center;
  margin: 1rem 0;
}
.fade-in {
  animation: fadeIn 0.4s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
