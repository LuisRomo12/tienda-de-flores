\<template>
  <header class="main-header">
    <div class="top-bar">
      <p>¡Envío gratis en pedidos mayores a $500! 🌸</p>
    </div>

    <nav class="navbar" aria-label="Navegación principal">
      <div class="logo">
        <a href="/">
          <span class="accent">UT</span>Flower
        </a>
      </div>

      <!-- Botón Secreto para Admin -->
      <button class="secret-admin-btn" @click="handleSecretAccess" title=""></button>

      <button 
        class="menu-toggle" 
        @click="isMobileMenuOpen = !isMobileMenuOpen"
        :aria-expanded="isMobileMenuOpen"
        aria-controls="nav-menu"
      >
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </button>

      <ul id="nav-menu" :class="['nav-links', { 'is-active': isMobileMenuOpen }]">
        <li><a href="/" class="active" v-magnetic="{ strength: 0.5 }">{{ $t('nav.inicio') }}</a></li>
        
        <li class="has-submenu" @mouseenter="openSubmenu('catalog')" @mouseleave="closeSubmenu">
          <a href="/catalogo" aria-haspopup="true" v-magnetic="{ strength: 0.5 }">{{ $t('nav.catalogo') }} ▾</a>
          <ul class="submenu" v-show="activeSubmenu === 'catalog'">
            <li><router-link to="/catalogo" v-magnetic="{ strength: 0.2 }">Todos</router-link></li>
            <li><router-link to="/catalogo?cat=Rosas" v-magnetic="{ strength: 0.2 }">Rosas</router-link></li>
            <li><router-link to="/catalogo?cat=Tulipanes" v-magnetic="{ strength: 0.2 }">Tulipanes</router-link></li>
            <li><router-link to="/catalogo?cat=Girasoles" v-magnetic="{ strength: 0.2 }">Girasoles</router-link></li>
            <li><router-link to="/catalogo?cat=Orquídeas" v-magnetic="{ strength: 0.2 }">Orquídeas</router-link></li>
            <li><router-link to="/catalogo?cat=Silvestres" v-magnetic="{ strength: 0.2 }">Silvestres</router-link></li>
            <li><router-link to="/catalogo?cat=Mixtas" v-magnetic="{ strength: 0.2 }">Mixtas</router-link></li>
          </ul>
        </li>

        <li><a href="/constructor" class="highlight" v-magnetic="{ strength: 0.8 }">Hazlo tú mismo</a></li>
        <li><a href="/nosotros" v-magnetic="{ strength: 0.5 }">{{ $t('nav.nosotros') }}</a></li>
        <li><a href="/contacto" v-magnetic="{ strength: 0.5 }">{{ $t('nav.contacto') }}</a></li>

        <div class="nav-icons">
          <!-- Botón de Modo Oscuro -->
          <button @click="toggleTheme" class="theme-toggle" :aria-label="isDarkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'" v-magnetic="{ strength: 0.5 }">
            {{ isDarkMode ? '☀️' : '🌙' }}
          </button>
          
          <a href="/buscar" aria-label="Buscar" v-magnetic="{ strength: 0.5 }"><i class="icon-search">🔍</i></a>
          <li class="has-submenu" @mouseenter="openSubmenu('user')" @mouseleave="closeSubmenu">
            <router-link to="/perfil" aria-label="Cuenta" v-magnetic="{ strength: 0.5 }">👤</router-link>
            <ul class="submenu" v-show="activeSubmenu === 'user'">
              <template v-if="!isLoggedIn">
                <li><router-link to="/login" @click="closeSubmenu">Iniciar Sesión</router-link></li>
                <li><router-link to="/registro" @click="closeSubmenu">Registrarse</router-link></li>
              </template>
              <template v-else>
                <li><router-link to="/perfil" @click="closeSubmenu">Mi Perfil</router-link></li>
                <li><a href="#" @click.prevent="logout">Cerrar Sesión</a></li>
              </template>
            </ul>
          </li>
          <a href="/carrito" class="cart-icon" aria-label="Carrito" v-magnetic="{ strength: 0.5 }">
            🛒 <span class="badge">0</span>
          </a>
        </div>
      </ul>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'Navbar',
  data() {
    return {
      isMobileMenuOpen: false,
      activeSubmenu: null,
      isDarkMode: false,
      isLoggedIn: false,
      secretClicks: 0,
      secretClickTimer: null
    };
  },
  mounted() {
    // Al cargar la navbar, leemos la preferencia del usuario en localStorage
    const savedTheme = localStorage.getItem('fori-theme');
    if (savedTheme === 'dark') {
      this.isDarkMode = true;
      document.body.classList.add('dark-theme');
    }

    // Comprobar si hay sesión iniciada
    this.checkLoginStatus();

    // Escuchar cambios en el login a través de un evento global o solo recargando
    // Para simplificar, si cambian de ruta suele recargarse o re-montarse
  },
  methods: {
    checkLoginStatus() {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      this.isLoggedIn = !!token;
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      this.isLoggedIn = false;
      this.$router.push('/registro');
    },
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
      if (this.isDarkMode) {
        document.body.classList.add('dark-theme');
        localStorage.setItem('fori-theme', 'dark');
      } else {
        document.body.classList.remove('dark-theme');
        localStorage.setItem('fori-theme', 'light');
      }
    },
    openSubmenu(menu) {
      this.activeSubmenu = menu;
    },
    closeSubmenu() {
      this.activeSubmenu = null;
    },
    async handleSecretAccess() {
      this.secretClicks++;
      clearTimeout(this.secretClickTimer);
      
      // Si no hace clic de nuevo en 2 segundos, se reinicia el contador
      this.secretClickTimer = setTimeout(() => {
        this.secretClicks = 0;
      }, 2000);

      // Si llegó a 7 clics rápidos:
      if (this.secretClicks === 7) {
        this.secretClicks = 0; // reset
        
        // Como Windows Hello no tiene el PIN habilitado para Passkeys en esta PC,
        // usamos nuestro propio candado interno (un prompt nativo del navegador).
        const pass = prompt('🤫 MODO ADMINISTRADOR DETECTADO\n\nPor favor, ingrese la Contraseña Maestra:');
        
        // Cambia 'admin123' por la contraseña que quieras configurar para entrar
        if (pass === 'admin123') {
            alert('✅ ¡Acceso Autorizado! \n\n Bienvenido al panel de control.');
            // Usamos una ruta "limpia" (clean URL) sin el index.html para que se vea profesional
            window.location.href = '/admin-inventario'; 
        } else if (pass !== null) {
            alert('❌ Acceso Denegado. Contraseña incorrecta.');
        }
      }
    }
  },
  watch: {
    // Re-chequear al cambiar de ruta
    '$route'() {
      this.checkLoginStatus();
    }
  }
};
</script>

<style scoped>
/* Las variables globales ahora provienen de src/css/base.css para soportar el modo oscuro. */

.main-header {
  background-color: var(--header-bg, #FDF9F1);
  box-shadow: var(--card-shadow, 0 4px 15px rgba(200, 100, 50, 0.08));
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid var(--primary-pink);
  transition: background-color 0.4s ease;
}

.top-bar {
  background-color: var(--primary-pink);
  color: var(--white);
  text-align: center;
  padding: 8px 0;
  font-size: 0.85rem;
  letter-spacing: 1px;
  font-weight: 500;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 5%;
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  font-size: 1.6rem;
  font-family: 'Playfair Display', serif; /* Sugerencia de fuente elegante */
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.logo a { color: var(--text-soft); text-decoration: none; }
.logo .accent { color: var(--accent-pink); }

/* Botón Secreto (Admin) */
.secret-admin-btn {
  background: none;
  border: none;
  cursor: pointer;
  width: 15px;
  height: 3px;
  background-color: var(--text-soft);
  opacity: 0.2; /* Muy sutil para que no llame la atención de los usuarios normales */
  margin-left: 15px;
  border-radius: 2px;
  transition: opacity 0.3s ease, background-color 0.3s ease;
}

.secret-admin-btn:hover {
  opacity: 1;
  background-color: var(--accent-pink);
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 30px;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: var(--text-soft);
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  display: inline-block; /* Necesario para transformaciones correctas de v-magnetic */
}

.nav-links a:hover, .active {
  color: var(--accent-pink);
  transform: translateY(-2px); /* Hover animado extra */
}

/* Submenús */
.has-submenu { position: relative; }

.submenu {
  position: absolute;
  top: 100%;
  left: 0;
  background: var(--header-bg, var(--bg-creme));
  box-shadow: 0 8px 20px var(--card-shadow, rgba(0,0,0,0.1));
  padding: 15px 0;
  min-width: 180px;
  list-style: none;
  border-radius: 4px;
  border-top: 4px solid var(--primary-pink);
  transition: background-color 0.4s ease;
}

.submenu li a {
  padding: 12px 25px;
  display: block;
  font-size: 0.85rem;
}

.submenu li a:hover {
  background-color: var(--primary-pink);
  color: var(--white);
}

/* Botón Especial "Hazlo tú mismo" */
.highlight {
  background-color: var(--header-bg, var(--bg-creme));
  border: 2px solid var(--accent-pink) !important;
  color: var(--accent-pink) !important;
  padding: 8px 20px;
  border-radius: 25px;
  text-transform: uppercase;
  font-size: 0.8rem !important;
  letter-spacing: 1px;
}

.highlight:hover {
  background-color: var(--accent-pink);
  color: var(--white) !important;
}

/* Theme Toggle Button */
.theme-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: transform 0.3s ease, background-color 0.3s ease;
  color: var(--text-soft);
}

.theme-toggle:hover {
  background-color: var(--primary-pink);
  transform: rotate(15deg) scale(1.1);
}

/* Iconos */
.nav-icons {
  display: flex;
  gap: 20px;
  align-items: center;
  color: var(--text-soft);
}

.badge {
  background-color: var(--accent-pink);
  color: white;
  padding: 2px 6px;
  border-radius: 50%;
  font-size: 0.7rem;
}

/* Toggle de Menú Móvil (Hamburguesa) */
.menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
}

.menu-toggle .bar {
  display: block;
  width: 25px;
  height: 3px;
  margin: 5px auto;
  background-color: var(--accent-pink);
  transition: all 0.3s ease;
  border-radius: 2px;
}

/* Móvil */
@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }

  .nav-links {
    display: none;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background-color: var(--header-bg, var(--bg-creme));
    border-top: 1px solid var(--primary-pink);
    padding: 20px 0;
    box-shadow: 0 10px 15px rgba(0,0,0,0.1);
  }

  .nav-links.is-active {
    display: flex;
  }

  .nav-icons {
    justify-content: center;
    margin-top: 15px;
  }
}
</style>