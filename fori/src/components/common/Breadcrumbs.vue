<template>
  <nav class="breadcrumb-nav" aria-label="Ruta de navegación">
    <ol class="breadcrumb-list">
      <li class="breadcrumb-item">
        <router-link to="/" class="breadcrumb-link">
          <span class="icon">🏠</span> Inicio
        </router-link>
      </li>
      <li v-for="(crumb, index) in breadcrumbs" :key="index" class="breadcrumb-item">
        <span class="separator">›</span>
        <router-link v-if="index < breadcrumbs.length - 1" :to="crumb.path" class="breadcrumb-link">
          {{ crumb.name }}
        </router-link>
        <span v-else class="current-step" aria-current="page">{{ crumb.name }}</span>
      </li>
    </ol>
  </nav>
</template>

<script>
export default {
  name: 'Breadcrumbs',
  computed: {
    breadcrumbs() {
      // 1. Obtenemos la ruta actual y eliminamos partes vacías
      const pathArray = this.$route.path.split('/').filter(p => p !== '');
      
      // 2. Construimos el arreglo de objetos para cada nivel
      return pathArray.map((path, index) => {
        // Creamos la ruta acumulada (ej. /catalogo/rosas)
        const fullPath = '/' + pathArray.slice(0, index + 1).join('/');
        
        return {
          // Formateamos el nombre (Mayúscula inicial y sin guiones)
          name: path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, ' '),
          path: fullPath
        };
      });
    }
  }
}
</script>

<style scoped>
.breadcrumb-nav {
  background-color: var(--header-bg, var(--bg-creme)); /* Fondo Crema (oscuro en modo oscuro) */
  padding: 12px 5%;
  border-bottom: 1px solid var(--primary-pink); /* Línea Rosa Pastel (o frambuesa en dark) */
  transition: background-color 0.4s ease, border-color 0.4s ease;
}
.breadcrumb-list {
  display: flex;
  align-items: center;
  list-style: none;
  gap: 8px;
  font-size: 0.9rem;
}
.breadcrumb-link {
  color: var(--accent-pink, #D1823C); /* Color Ocre/Rosa */
  text-decoration: none;
  font-weight: 500;
  transition: color 0.4s ease;
}
.separator {
  color: var(--text-soft, #B7B16B); /* Verde Oliva -> adapta a texto */
  font-weight: bold;
  margin: 0 4px;
}
.current-step {
  color: var(--text-primary, #D26259); /* Rosa Intenso para la página actual */
  font-weight: bold;
  transition: color 0.4s ease;
}
</style>