<template>
  <div class="settings-page">
    <div class="settings-container">
      <h1 class="page-title">Configuración de Cuenta</h1>
      
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <div class="tab-content">
        <!-- TAB SEGURIDAD -->
        <div v-if="activeTab === 'seguridad'" class="tab-pane">
          <h2>Seguridad</h2>
          <div class="card">
            <h3>Cambiar Contraseña</h3>
            <form @submit.prevent="changePassword" class="settings-form">
              <div class="form-group">
                <label>Contraseña Actual</label>
                <input type="password" v-model="passForm.old_password" required />
              </div>
              <div class="form-group">
                <label>Nueva Contraseña</label>
                <input type="password" v-model="passForm.new_password" required />
              </div>
              <button type="submit" class="btn-primary" :disabled="loading.pass">
                {{ loading.pass ? 'Guardando...' : 'Actualizar Contraseña' }}
              </button>
            </form>
          </div>

          <div class="card mt-4">
            <h3>Autenticación en Dos Pasos (MFA)</h3>
            <p>Añade una capa extra de seguridad a tu cuenta.</p>
            
            <div v-if="preferences.mfa_enabled">
              <span class="badge success">MFA Activado</span>
              <button @click="disableMFA" class="btn-danger mt-2" :disabled="loading.mfa">
                Desactivar MFA
              </button>
            </div>
            <div v-else>
              <span class="badge warning">MFA Desactivado</span>
              <button @click="enableMFA" class="btn-secondary mt-2" :disabled="loading.mfa">
                Configurar MFA
              </button>
            </div>
          </div>

          <!-- Nueva Card: Pregunta Secreta -->
          <div class="card mt-4">
            <h3>Pregunta de Seguridad</h3>
            <p>Configura una interrogante para recuperar tu contraseña si la olvidas.</p>
            <form @submit.prevent="saveSecurityQuestion" class="settings-form mt-2">
              <div class="form-group">
                <label>Pregunta (Ej: ¿Nombre de mi primer mascota?)</label>
                <input type="text" v-model="questForm.pregunta" placeholder="Escribe la interrogante" required />
              </div>
              <div class="form-group">
                <label>Respuesta Oculta</label>
                <input type="password" v-model="questForm.respuesta" placeholder="Escribe la palabra secreta" required />
              </div>
              <button type="submit" class="btn-primary" :disabled="loading.quest">
                {{ loading.quest ? 'Guardando...' : 'Fijar Pregunta' }}
              </button>
            </form>
          </div>
        </div>

        <!-- TAB SESIONES -->
        <div v-if="activeTab === 'sesiones'" class="tab-pane">
          <h2>Sesiones Activas</h2>
          <p>Revisa en qué dispositivos has iniciado sesión recientemente.</p>
          
          <div v-if="sessions.length === 0" class="empty-state">
            Cargando sesiones...
          </div>
          
          <div class="sessions-list">
            <div v-for="ses in sessions" :key="ses.id" class="session-card">
              <div class="session-info">
                <div class="device-name">
                  {{ ses.device }}
                  <span v-if="ses.is_current" class="badge success" style="margin-left: 8px;">Sesión Actual</span>
                </div>
                <div class="ip-address">IP: {{ ses.ip_address }}</div>
                <div class="dates">
                  Iniciada: {{ new Date(ses.created_at).toLocaleString('es-MX') }}
                </div>
              </div>
              <button v-if="!ses.is_current" @click="revokeSession(ses.id)" class="btn-outline-danger">
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>

        <!-- TAB PREFERENCIAS -->
        <div v-if="activeTab === 'preferencias'" class="tab-pane">
          <h2>{{ $t('prefs.title') }}</h2>
          <div class="card">
            <form @submit.prevent="savePreferences" class="settings-form">
              <div class="form-group">
                <label>{{ $t('prefs.theme') }}</label>
                <select v-model="prefForm.tema">
                  <option value="claro">{{ $t('prefs.light') }}</option>
                  <option value="oscuro">{{ $t('prefs.dark') }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>{{ $t('prefs.language') }}</label>
                <select v-model="prefForm.idioma">
                  <option value="es">{{ $t('prefs.spanish') }}</option>
                  <option value="en">{{ $t('prefs.english') }}</option>
                </select>
              </div>
              <button type="submit" class="btn-primary" :disabled="loading.pref">
                {{ $t('prefs.save') }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- Notificaciones -->
      <transition name="fade">
        <div v-if="notification.show" :class="['global-notification', notification.type]">
          {{ notification.message }}
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/axios';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { locale, t } = useI18n();
const activeTab = ref('seguridad');

const tabs = [
  { id: 'seguridad', name: 'Seguridad' },
  { id: 'sesiones', name: 'Sesiones Activas' },
  { id: 'preferencias', name: 'Preferencias' }
];

const passForm = ref({ old_password: '', new_password: '' });
const prefForm = ref({ tema: 'claro', idioma: 'es' });
const questForm = ref({ pregunta: '', respuesta: '' });
const preferences = ref({ mfa_enabled: false });
const sessions = ref([]);

const loading = ref({ pass: false, mfa: false, pref: false, quest: false });
const notification = ref({ show: false, message: '', type: 'success' });

const showNotify = (msg, type = 'success') => {
  notification.value = { show: true, message: msg, type };
  setTimeout(() => { notification.value.show = false; }, 4000);
};

onMounted(async () => {
  await fetchPreferences();
  await fetchSessions();
});

const fetchPreferences = async () => {
  try {
    const { data } = await apiClient.get('/api/users/me/preferences');
    preferences.value.mfa_enabled = data.mfa_enabled;
    prefForm.value.tema = data.tema || 'claro';
    prefForm.value.idioma = data.idioma || 'es';
    locale.value = prefForm.value.idioma;
  } catch (err) {
    console.error("Error obteniendo preferencias", err);
  }
};

const fetchSessions = async () => {
  try {
    const { data } = await apiClient.get('/api/users/me/sessions');
    sessions.value = data;
  } catch (err) {
    console.error("Error obteniendo sesiones", err);
  }
};

const changePassword = async () => {
  loading.value.pass = true;
  try {
    await apiClient.put('/api/users/me/password', passForm.value);
    showNotify('Contraseña actualizada correctamente');
    passForm.value = { old_password: '', new_password: '' };
  } catch (err) {
    showNotify(err.response?.data?.detail || 'Error al cambiar contraseña', 'error');
  } finally {
    loading.value.pass = false;
  }
};

const enableMFA = () => {
  // Configuro MFA mandando a la vista existente
  router.push('/mfa');
};

const disableMFA = async () => {
  if (!confirm('¿Estás seguro de que deseas desactivar la autenticación de dos factores? Esto reducirá drásticamente la seguridad de tu cuenta.')) return;
  
  loading.value.mfa = true;
  try {
    await apiClient.post('/api/users/me/mfa/toggle');
    preferences.value.mfa_enabled = false;
    showNotify('MFA desactivado correctamente');
  } catch (err) {
    showNotify('Error al desactivar MFA', 'error');
  } finally {
    loading.value.mfa = false;
  }
};

const saveSecurityQuestion = async () => {
  loading.value.quest = true;
  try {
    await apiClient.post('/api/auth/users/me/security-question', questForm.value);
    showNotify('Pregunta configurada correctamente y encriptada.');
    questForm.value = { pregunta: '', respuesta: '' };
  } catch (err) {
    showNotify('Error al guardar la pregunta secreta', 'error');
  } finally {
    loading.value.quest = false;
  }
};

const revokeSession = async (sessionId) => {
  try {
    await apiClient.delete(`/api/users/me/sessions/${sessionId}`);
    sessions.value = sessions.value.filter(s => s.id !== sessionId);
    showNotify('Sesión cerrada correctamente');
  } catch (err) {
    showNotify('Error al cerrar la sesión', 'error');
  }
};

const savePreferences = async () => {
  loading.value.pref = true;
  try {
    await apiClient.put('/api/users/me/preferences', prefForm.value);
    showNotify(t('prefs.success'));
    locale.value = prefForm.value.idioma;
    // Integración de tema en el frontend
    if (prefForm.value.tema === 'oscuro') {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  } catch (err) {
    showNotify(t('prefs.error'), 'error');
  } finally {
    loading.value.pref = false;
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

.settings-page {
  font-family: 'Inter', sans-serif;
  background-color: #faf7f5;
  min-height: 100vh;
  padding: 40px 20px;
  color: #333;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.page-title {
  font-family: 'Playfair Display', serif;
  font-size: 32px;
  color: #c08497;
  margin-bottom: 30px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e2d5d8;
  padding-bottom: 1px;
}

.tab-btn {
  background: none;
  border: none;
  padding: 12px 20px;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: #c08497;
}

.tab-btn.active {
  color: #c08497;
  border-bottom-color: #c08497;
}

.tab-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.tab-pane h2 {
  font-family: 'Playfair Display', serif;
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.card {
  background: #fdfbfb;
  border: 1px solid #f0e6e8;
  border-radius: 8px;
  padding: 24px;
}

.card h3 {
  font-size: 18px;
  margin-bottom: 16px;
  color: #444;
}

.settings-form .form-group {
  margin-bottom: 16px;
}

.settings-form label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
  font-weight: 500;
}

.settings-form input,
.settings-form select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2d5d8;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
  background: white;
}

.settings-form input:focus,
.settings-form select:focus {
  border-color: #c08497;
}

.btn-primary {
  background-color: #c08497;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
  width: 100%;
  margin-top: 10px;
}

.btn-primary:hover:not(:disabled) {
  background-color: #ab7184;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: white;
  color: #c08497;
  border: 1px solid #c08497;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background-color: #faf7f5;
}

.btn-danger {
  background-color: #e57373;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-outline-danger {
  background-color: transparent;
  color: #e57373;
  border: 1px solid #e57373;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline-danger:hover {
  background-color: #fff0f0;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.badge.warning {
  background-color: #fff8e1;
  color: #f57f17;
}

.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 24px; }

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 20px;
}

.session-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e2d5d8;
  border-radius: 8px;
  background: #fdfbfb;
}

.device-name {
  font-weight: 600;
  color: #333;
  font-size: 15px;
}

.ip-address {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.dates {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.global-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 1000;
}

.global-notification.success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border-left: 4px solid #4caf50;
}

.global-notification.error {
  background-color: #ffebee;
  color: #c62828;
  border-left: 4px solid #ef5350;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
