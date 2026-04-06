<template>
  <div id="app">
    <FlowerCursor />
    <Navbar /> 
    
    <breadcrumbs /> 

    <main>
      <router-view /> 
    </main>

    <Footer />
    
    <!-- Componente Global del Reto Final (Parte 6) -->
    <LiveNotifications />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useI18n } from 'vue-i18n'
import apiClient from './api/axios'

import FlowerCursor from './components/common/FlowerCursor.vue'
import Navbar from './components/common/Navbar.vue'
import Footer from './components/common/Footer.vue'
import breadcrumbs from './components/common/Breadcrumbs.vue' 
import LiveNotifications from './components/common/LiveNotifications.vue' 

export default {
  components: {
    FlowerCursor,
    Navbar,
    Footer,
    breadcrumbs, 
    LiveNotifications 
  },
  setup() {
    const authStore = useAuthStore()
    const { locale } = useI18n()

    onMounted(async () => {
      // 1. Set global i18n locale from Backend Preferences on page load
      try {
        const prefRes = await apiClient.get('/api/users/me/preferences')
        if (prefRes.data && prefRes.data.idioma) {
          locale.value = prefRes.data.idioma
        }
      } catch (err) {
        // It will fail silently if user is not logged in, which is fine
      }

      // SSO SILENT LOGIN: App B (o refresco)
      if (!authStore.state.accessToken) {
        try {
          // El interceptor de axios tiene withCredentials: true, enviará la cookie HttpOnly
          // Si expira o es 401, el interceptor llama a /api/auth/refresh, obtiene token y reintenta
          const res = await apiClient.get('/api/auth/me')
          
          if (res.data && res.data.email) {
            // Usuario validado con la sesión SSO
            authStore.setUser(res.data)
            alert("¡Sesión iniciada automáticamente vía SSO!")
          }
        } catch (error) {
          console.log("SSO silente falló o no existe sesión activa.")
        }
      }
    })

    return {}
  }
}
</script>