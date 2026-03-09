<template>
  <div class="profile-layout min-h-screen bg-gray-50 dark:bg-gray-900 pb-12">
    
    <!-- Contenido cuando el usuario ha iniciado sesión -->
    <div v-if="isLoggedIn">
      <!-- Header tipo MercadoLibre (Amarillo o adaptable al DarkMode) -->
      <div class="profile-header bg-yellow-400 dark:bg-yellow-600 text-gray-900 dark:text-white py-8 px-5">
        <div class="max-w-6xl mx-auto flex items-center gap-6">
          <div class="avatar shadow-md">
            {{ userInitials }}
          </div>
          <div>
            <h1 class="text-2xl font-bold">{{ userName }}</h1>
            <p class="text-sm opacity-90">{{ userEmail }}</p>
          </div>
        </div>
      </div>

      <!-- Contenedor Principal Tablero -->
      <main class="max-w-6xl mx-auto px-5 -mt-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          
          <!-- Tarjeta: Información Personal -->
          <div class="dashboard-card group">
            <div class="card-icon bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300">
              👤
            </div>
            <div>
              <h2 class="card-title">Información personal</h2>
              <p class="card-desc">Actualiza tus datos y personaliza tu perfil.</p>
            </div>
            <button class="action-btn">Editar</button>
          </div>

          <!-- Tarjeta: Direcciones -->
          <div class="dashboard-card group" @click="goTo('/user/addresses')">
            <div class="card-icon bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300">
              📍
            </div>
            <div>
              <h2 class="card-title">Direcciones</h2>
              <p class="card-desc">Direcciones guardadas para tus envíos.</p>
            </div>
            <button class="action-btn">Gestionar</button>
          </div>


          <!-- Tarjeta: Historial de Compras -->
          <div class="dashboard-card group">
            <div class="card-icon bg-purple-100 text-purple-600 dark:bg-purple-900 dark:text-purple-300">
              🛍️
            </div>
            <div>
              <h2 class="card-title">Mis compras</h2>
              <p class="card-desc">Revisa el historial de tus pedidos y facturas.</p>
            </div>
            <button class="action-btn">Ver todas</button>
          </div>

          <!-- Tarjeta: Mi Carrito -->
          <div class="dashboard-card group" @click="goTo('/carrito')">
            <div class="card-icon bg-orange-100 text-orange-600 dark:bg-orange-900 dark:text-orange-300">
              🛒
            </div>
            <div>
              <h2 class="card-title">Mi carrito</h2>
              <p class="card-desc">Tienes productos esperando por ti.</p>
            </div>
            <button class="action-btn">Ir al Carrito</button>
          </div>

          <!-- Tarjeta: Seguridad (Contraseña) -->
          <div class="dashboard-card group">
            <div class="card-icon bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-300">
              🔒
            </div>
            <div>
              <h2 class="card-title">Seguridad</h2>
              <p class="card-desc">Modifica tu contraseña y mantén tu cuenta segura.</p>
            </div>
            <button class="action-btn">Modificar</button>
          </div>

          <!-- Tarjeta: Volver al Inicio -->
          <div class="dashboard-card group cursor-pointer border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-yellow-400" @click="goTo('/')">
            <div class="card-icon bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300">
              🏠
            </div>
            <div>
              <h2 class="card-title">Ir al Inicio</h2>
              <p class="card-desc">Regresa a la pantalla principal de la tienda.</p>
            </div>
          </div>

        </div>
      </main>
    </div>

    <!-- Contenido cuando el usuario NO ha iniciado sesión -->
    <div v-else class="empty-container">
      <div class="empty-card">
        <div class="empty-icon-wrapper">
          <span class="empty-icon">
            🌺
          </span>
        </div>
        <h2 class="empty-title">
          ¡Hola! Para ver tu perfil, <br/>ingresa a tu cuenta
        </h2>
        <p class="empty-desc">
          Podrás ver tus compras, editar tus datos, gestionar tus direcciones favoritas y mucho más.
        </p>
        
        <div class="empty-actions">
          <button @click="goTo('/login')" class="btn-primary">
            Iniciar sesión
          </button>
          <button @click="goTo('/registro')" class="btn-secondary">
            Crear cuenta nueva
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const userEmail = ref('');
const userName = ref('');
const isLoggedIn = ref(false);

onMounted(() => {
  // Intentar recuperar info del usuario del LocalStorage
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      const parsed = JSON.parse(storedUser);
      userEmail.value = parsed.email || userEmail.value;
      // Por defecto el backend solo devuelve el email, usaremos la primera parte del email o "Cliente"  
      userName.value = parsed.email ? parsed.email.split('@')[0] : 'Cliente';
      isLoggedIn.value = true;
    } catch (e) {
      isLoggedIn.value = false;
    }
  } else {
    isLoggedIn.value = false;
  }
});

const userInitials = computed(() => {
  if (userName.value) {
    return userName.value.substring(0, 2).toUpperCase();
  }
  return 'US';
});

const goTo = (path) => {
  router.push(path);
};
</script>

<style scoped>
/* Reset base styles for component */
.profile-layout {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Avatar circular tipo Google/MercadoLibre */
.avatar {
  background-color: white;
  color: #333;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
}

.dark-theme .avatar {
  background-color: #374151; /* gray-700 */
  color: #f3f4f6; /* gray-100 */
}

/* Sistema de Grid - Replicando ML layout */
.dashboard-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.2s ease-in-out;
  position: relative;
  overflow: hidden;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.dark-theme .dashboard-card {
  background-color: #1f2937; /* gray-800 */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
}

/* Iconos de las tarjetas */
.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #111827; /* gray-900 */
  margin-bottom: 4px;
}

.dark-theme .card-title {
  color: #f9fafb; /* gray-50 */
}

.card-desc {
  font-size: 0.875rem;
  color: #6b7280; /* gray-500 */
  line-height: 1.4;
}

.dark-theme .card-desc {
  color: #9ca3af; /* gray-400 */
}

/* Botones de Acción (Ocultos hasta hover para limpieza de interfaz) */
.action-btn {
  margin-top: auto;
  color: #3b82f6; /* blue-500 */
  font-weight: 600;
  font-size: 0.9rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.action-btn:hover {
  color: #1d4ed8; /* blue-700 */
  text-decoration: underline;
}

.dark-theme .action-btn {
  color: #60a5fa; /* blue-400 */
}

.dark-theme .action-btn:hover {
  color: #93c5fd; /* blue-300 */
}

/* Estilos para estado vacío (No iniciado sesión) */
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: 3rem 1.25rem;
}

.empty-card {
  background-color: white;
  padding: 2.5rem;
  border-radius: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 32rem;
  width: 100%;
  text-align: center;
  border: 1px solid #ffe4e6; /* rose-100 */
}

.dark-theme .empty-card {
  background-color: #1f2937; /* gray-800 */
  border-color: rgba(136, 19, 55, 0.3); /* rose-900/30 */
}

.empty-icon-wrapper {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.empty-icon {
  background-color: #fff1f2; /* rose-50 */
  width: 8rem;
  height: 8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  font-size: 3.5rem;
}

.dark-theme .empty-icon {
  background-color: rgba(136, 19, 55, 0.2); /* rose-900/20 */
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827; /* gray-900 */
  margin-bottom: 0.75rem;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.dark-theme .empty-title {
  color: #ffffff;
}

@media (min-width: 768px) {
  .empty-title {
    font-size: 1.875rem;
  }
}

.empty-desc {
  color: #6b7280; /* gray-500 */
  margin-bottom: 2rem;
  max-width: 28rem;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.625;
}

.dark-theme .empty-desc {
  color: #9ca3af; /* gray-400 */
}

.empty-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 0.5rem;
}

.btn-primary {
  width: 100%;
  background-color: #f43f5e; /* rose-500 */
  color: white;
  font-weight: 600;
  padding: 0.875rem 1.5rem;
  border-radius: 0.75rem;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary:hover {
  background-color: #e11d48; /* rose-600 */
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.btn-primary:active {
  background-color: #be123c; /* rose-700 */
}

.btn-secondary {
  width: 100%;
  background-color: white;
  color: #f43f5e; /* rose-500 */
  font-weight: 600;
  padding: 0.875rem 1.5rem;
  border-radius: 0.75rem;
  transition: all 0.2s;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 2px solid #f43f5e; /* rose-500 */
  cursor: pointer;
  font-size: 1rem;
}

.btn-secondary:hover {
  background-color: #fff1f2; /* rose-50 */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.dark-theme .btn-secondary {
  background-color: #1f2937; /* gray-800 */
  color: #fb7185; /* rose-400 */
  border-color: #fb7185; /* rose-400 */
}

.dark-theme .btn-secondary:hover {
  background-color: #374151; /* gray-700 */
}

/* Utilidades de Tailwind Emuladas para este componente */
.min-h-screen { min-height: 100vh; }
.pb-12 { padding-bottom: 3rem; }
.py-8 { padding-top: 2rem; padding-bottom: 2rem; }
.px-5 { padding-left: 1.25rem; padding-right: 1.25rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-6xl { max-width: 72rem; }
.flex { display: flex; }
.items-center { align-items: center; }
.gap-6 { gap: 1.5rem; }
.gap-4 { gap: 1rem; }
.-mt-6 { margin-top: -1.5rem; }
.shadow-md { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.font-bold { font-weight: 700; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.opacity-90 { opacity: 0.9; }

.grid { display: grid; }
.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
@media (min-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 1024px) {
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

/* Colores Base y Dark Mode */
.bg-gray-50 { background-color: #f9fafb; }
.dark-theme .dark\:bg-gray-900 { background-color: #111827; }

.bg-yellow-400 { background-color: #facc15; }
.dark-theme .dark\:bg-yellow-600 { background-color: #ca8a04; }

.text-gray-900 { color: #111827; }
.dark-theme .dark\:text-white { color: #ffffff; }

/* Icon Colors */
.bg-blue-100 { background-color: #dbeafe; }
.text-blue-600 { color: #2563eb; }
.dark-theme .dark\:bg-blue-900 { background-color: #1e3a8a; }
.dark-theme .dark\:text-blue-300 { color: #93c5fd; }

.bg-green-100 { background-color: #dcfce3; }
.text-green-600 { color: #16a34a; }
.dark-theme .dark\:bg-green-900 { background-color: #14532d; }
.dark-theme .dark\:text-green-300 { color: #86efac; }

.bg-purple-100 { background-color: #f3e8ff; }
.text-purple-600 { color: #9333ea; }
.dark-theme .dark\:bg-purple-900 { background-color: #581c87; }
.dark-theme .dark\:text-purple-300 { color: #d8b4fe; }

.bg-orange-100 { background-color: #ffedd5; }
.text-orange-600 { color: #ea580c; }
.dark-theme .dark\:bg-orange-900 { background-color: #7c2d12; }
.dark-theme .dark\:text-orange-300 { color: #fdba74; }

.bg-red-100 { background-color: #fee2e2; }
.text-red-600 { color: #dc2626; }
.dark-theme .dark\:bg-red-900 { background-color: #7f1d1d; }
.dark-theme .dark\:text-red-300 { color: #fca5a5; }

.bg-gray-100 { background-color: #f3f4f6; }
.text-gray-600 { color: #4b5563; }
.dark-theme .dark\:bg-gray-700 { background-color: #374151; }
.dark-theme .dark\:text-gray-300 { color: #d1d5db; }

.cursor-pointer { cursor: pointer; }
.border-2 { border-width: 2px; }
.border-dashed { border-style: dashed; }
.border-gray-300 { border-color: #d1d5db; }
.dark-theme .dark\:border-gray-600 { border-color: #4b5563; }
.hover\:border-yellow-400:hover { border-color: #facc15; }
</style>
