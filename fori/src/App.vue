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
import FlowerCursor from './components/common/FlowerCursor.vue'
import Navbar from './components/common/Navbar.vue'
import Footer from './components/common/Footer.vue'
import breadcrumbs from './components/common/Breadcrumbs.vue' //
import LiveNotifications from './components/common/LiveNotifications.vue' // Reto Final

export default {
  components: {
    FlowerCursor,
    Navbar,
    Footer,
    breadcrumbs, //
    LiveNotifications //
  }
}
</script>