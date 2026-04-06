<template>
  <div class="register-page" style="padding: 40px; max-width: 400px; margin: auto;">
    <h1>Registro de Usuario</h1>
    
    <form @submit.prevent="handleRegister" style="display: flex; flex-direction: column; gap: 15px;">
      
      <div class="field">
        <label>Correo Electrónico:</label>
        <input type="email" v-model="email" required placeholder="usuario@correo.com" style="padding: 8px;"/>
        <p v-if="errors.email" style="color: red; font-size: 0.8em;">{{ errors.email }}</p>
      </div>

      <div class="field">
        <label>Contraseña:</label>
        <input type="password" v-model="password" required pattern=".{8,}" placeholder="Mínimo 8 caracteres" style="padding: 8px;"/>
      </div>

      <div class="field">
        <label>Confirmar Contraseña:</label>
        <input type="password" v-model="confirmPassword" required placeholder="Repite tu contraseña" style="padding: 8px;"/>
        <p v-if="errors.match" style="color: red; font-size: 0.8em;">{{ errors.match }}</p>
      </div>

      <div class="captcha-box" style="margin-top: 10px; padding: 15px; border: 2px solid #D1823C; border-radius: 5px; background-color: #fff9f4;">
        <label style="font-weight: bold; display: block; margin-bottom: 8px; color: #333;">
          Desafío Humano: ¿Cuánto es 5 + 3?
        </label>
        <input 
          type="number" 
          v-model="captchaAnswer" 
          required 
          placeholder="Escribe el resultado"
          style="padding: 10px; width: 100%; border: 1px solid #ccc; box-sizing: border-box;"
        />
        <p v-if="errors.captcha" style="color: red; font-size: 0.9em; font-weight: bold; margin-top: 5px;">
          {{ errors.captcha }} 
        </p>
      </div>

      <button type="submit" style="padding: 12px; background: #D1823C; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 10px;">
        Finalizar Registro
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const captchaAnswer = ref('');
const errors = ref({ email: '', match: '', captcha: '' });

const handleRegister = async () => {
  // Limpiar errores previos
  errors.value = { email: '', match: '', captcha: '' };

  // Validaciones locales
  if (password.value !== confirmPassword.value) {
    errors.value.match = "Las contraseñas no coinciden.";
    return;
  }

  if (parseInt(captchaAnswer.value) !== 8) {
    errors.value.captcha = "Respuesta de desafío incorrecta.";
    return;
  }

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        confirm_password: confirmPassword.value,
        captcha_answer: parseInt(captchaAnswer.value)
      })
    });

    const data = await response.json();

    if (response.ok) {
      alert("¡Registro guardado en la base de datos!");
      // Limpiar formulario
      email.value = ''; password.value = ''; confirmPassword.value = ''; captchaAnswer.value = '';
    } else {
      // Mostrar error del backend (ej. correo duplicado)
      alert("Error: " + (data.detail || "No se pudo registrar"));
    }
  } catch (error) {
    alert("Error de conexión con el servidor backend.");
  }
};
</script>