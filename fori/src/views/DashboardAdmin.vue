<template>
  <div class="dashboard-admin">
    <div class="dashboard-header">
      <h1>Panel Administrativo</h1>
      <p>Gestión de Usuarios y Publicaciones (Demostración Parte 2)</p>
    </div>

    <!-- Buscador con Debounce Puro -->
    <div class="search-bar">
      <input 
        type="text" 
        :value="searchQuery"
        @input="handleInputDebounced"
        placeholder="Buscar usuarios o publicaciones..."
        class="search-input"
      />
      <span class="search-info">Filtrado en tiempo real con Debounce puro (300ms)</span>
    </div>

    <!-- Indicador de Carga (Loader) CSS puro -->
    <div v-if="loading" class="loader-container">
      <div class="pure-css-loader"></div>
      <p>Cargando datos asíncronos simultáneos (Promise.all)...</p>
    </div>

    <!-- Manejo Visual de Errores -->
    <div v-if="errorMsg" class="error-banner">
      <div class="error-icon">⚠️</div>
      <div class="error-content">
        <h3>Error en la Carga de Datos</h3>
        <p>{{ errorMsg }}</p>
        <button @click="cargarDatos(true)" class="retry-btn">Reintentar con API Fallida (Simular Error)</button>
        <button @click="cargarDatos(false)" class="retry-btn success">Reintentar con API Correcta</button>
      </div>
    </div>

    <!-- Tablas Dinámicas (Renderizado si hay datos y no hay error grave) -->
    <div v-if="!loading && !errorMsg" class="dashboard-content">

      <!-- Columna Usuarios -->
      <div class="dashboard-card">
        <h2>Usuarios ({{ filteredUsers.length }})</h2>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Email</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>#{{ user.id }}</td>
                <td>{{ user.name }}</td>
                <td>{{ user.email }}</td>
              </tr>
              <tr v-if="filteredUsers.length === 0">
                <td colspan="3" class="text-center">No hay usuarios coincidentes.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Columna Publicaciones (Posts) -->
      <div class="dashboard-card">
        <h2>Publicaciones ({{ filteredPosts.length }})</h2>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Autor (User ID)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="post in filteredPosts" :key="post.id">
                <td>#{{ post.id }}</td>
                <td class="text-capitalize">{{ post.title }}</td>
                <td>#{{ post.userId }}</td>
              </tr>
              <tr v-if="filteredPosts.length === 0">
                <td colspan="3" class="text-center">No hay publicaciones coincidentes.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
// Función Debounce pura para cumplir requisito estricto
function debounce(fn, delay) {
   let timeout;
   return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn(...args), delay);
   };
}

export default {
  name: 'DashboardAdmin',
  data() {
    return {
      users: [],
      posts: [],
      loading: true,
      errorMsg: null,
      searchQuery: '',
      debouncedSearchQuery: '',
      // Guardamos la referencia de la función debounced
      debounceFn: null
    }
  },
  computed: {
    filteredUsers() {
      const q = this.debouncedSearchQuery.toLowerCase();
      if (!q) return this.users;
      return this.users.filter(u => 
        u.name.toLowerCase().includes(q) || 
        u.email.toLowerCase().includes(q)
      );
    },
    filteredPosts() {
      const q = this.debouncedSearchQuery.toLowerCase();
      if (!q) return this.posts;
      return this.posts.filter(p => 
        p.title.toLowerCase().includes(q)
      );
    }
  },
  created() {
    // Inicializar debounce wrapper
    this.debounceFn = debounce((val) => {
      this.debouncedSearchQuery = val;
    }, 300);
  },
  mounted() {
    // Cargar con éxito por defecto al abrir
    this.cargarDatos(false);
  },
  methods: {
    handleInputDebounced(event) {
      // Actualizamos el value original instantáneamente en el input
      this.searchQuery = event.target.value;
      // Llamamos a la función debounced que actualizará debouncedSearchQuery en 300ms
      this.debounceFn(event.target.value);
    },

    async cargarDatos(simularFallo = false) {
      this.loading = true;
      this.errorMsg = null;
      this.users = [];
      this.posts = [];

      try {
        // PARTE 2: "Múltiples peticiones simultáneas. Debe usar: Promise.all()"
        
        // El endpoint URL cambiará dependiendo de si queremos forzar el fallo
        const postsUrl = simularFallo 
          ? 'https://jsonplaceholder.typicode.com/posts_FAKE_ENDPOINT_ERR' 
          : 'https://jsonplaceholder.typicode.com/posts';
          
        const [usersResponse, postsResponse] = await Promise.all([
          fetch('https://jsonplaceholder.typicode.com/users'),
          fetch(postsUrl)
        ]);

        // Verificamos estado (Fetch no lanza error 404 por red directamente)
        if (!usersResponse.ok) throw new Error(`Error Usuarios: ${usersResponse.status}`);
        if (!postsResponse.ok) throw new Error(`Error Publicaciones: ${postsResponse.status} Endpoint caído.`);

        // Solo se ejecutan si ambas promesas pasaron bien
        const usersData = await usersResponse.json();
        const postsData = await postsResponse.json();

        this.users = usersData;
        this.posts = postsData;

      } catch (err) {
        // Análisis de Falla: Si UNA solicitud falla, todo el bloque Promise.all() entra en catch
        console.error("Fallo general detectado:", err);
        this.errorMsg = "No se pudieron recuperar todos los módulos del Dashboard. " + 
          (simularFallo ? "Como simulamos un fallo en /posts, Promise.all abortó la asignación de /users demostrando el principio de 'Todo o Nada'." : err.message);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.dashboard-admin {
  padding: 40px;
  background-color: var(--bg-creme, #FDF9F1);
  min-height: 80vh;
  font-family: 'Inter', sans-serif;
  color: var(--text-soft);
  transition: background-color 0.4s ease, color 0.4s ease;
}

.dashboard-header {
  margin-bottom: 30px;
  text-align: center;
}

.dashboard-header h1 {
  color: var(--accent-pink, #D26259);
  font-family: 'Playfair Display', serif;
  margin-bottom: 5px;
}

.search-bar {
  max-width: 600px;
  margin: 0 auto 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.search-input {
  width: 100%;
  padding: 12px 20px;
  border: 2px solid var(--primary-pink, #F4B8C1);
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  background-color: var(--card-bg, #fff);
  color: var(--text-soft);
  transition: box-shadow 0.3s ease, background-color 0.4s ease;
}

.search-input:focus {
  box-shadow: 0 0 10px rgba(244, 184, 193, 0.5);
}

.search-info {
  font-size: 0.8rem;
  color: #888;
}

/* CARGADOR (LOADER) CSS PURO */
.loader-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 0;
  color: #D1823C;
}

.pure-css-loader {
  border: 5px solid rgba(209, 130, 60, 0.2);
  border-top: 5px solid #D1823C;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* MANEJO VISUAL DE ERRORES */
.error-banner {
  background: #fff0f0;
  border-left: 6px solid #e74c3c;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto 30px;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.1);
}

.error-icon {
  font-size: 2.5rem;
}

.error-content h3 {
  color: #c0392b;
  margin-top: 0;
  margin-bottom: 10px;
}

.retry-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 10px;
  margin-top: 15px;
  transition: opacity 0.2s;
}

.retry-btn:hover {
  opacity: 0.9;
}

.retry-btn.success {
  background: #27ae60;
}

/* GRILILLAS DE TABLAS */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.dashboard-card {
  background: var(--card-bg, white);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px var(--card-shadow, rgba(0,0,0,0.05));
  transition: background-color 0.4s ease, box-shadow 0.4s ease;
}

.dashboard-card h2 {
  color: var(--text-soft, #5A4A42);
  margin-top: 0;
  border-bottom: 2px solid var(--border-color, #FDF9F1);
  padding-bottom: 10px;
}

.table-responsive {
  max-height: 500px;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 40px 15px;
  text-align: left;
  border-bottom: 1px solid var(--border-color, #eee);
  font-size: 0.95rem;
}

th {
  background: var(--bg-creme, #FAFAFA);
  position: sticky;
  top: 0;
  color: var(--accent-pink, #D1823C);
}

.text-center { text-align: center; color: #888; }
.text-capitalize { text-transform: capitalize; }

@media (max-width: 900px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

/* --- DARK MODE OVERRIDES --- */
:global(body.dark-theme) .dashboard-admin { background-color: #121212; }
:global(body.dark-theme) .dashboard-header h1 { color: #f8fafc; }
:global(body.dark-theme) .dashboard-header p { color: #94a3b8; }
:global(body.dark-theme) .search-input { background-color: #1e1e1e; color: #f8fafc; border-color: #333; }
:global(body.dark-theme) .search-input:focus { border-color: #D66D81; box-shadow: 0 0 10px rgba(214, 109, 129, 0.3); }
:global(body.dark-theme) .dashboard-card { background: #1e1e1e; box-shadow: 0 4px 15px rgba(255,255,255,0.02); border: 1px solid #333; }
:global(body.dark-theme) .dashboard-card h2 { color: #f8fafc; border-bottom-color: #333; }
:global(body.dark-theme) th { background: #1A1A1A; color: #D66D81; border-bottom-color: #333; }
:global(body.dark-theme) td { border-bottom-color: #333; color: #e2e8f0; }
:global(body.dark-theme) .retry-btn { background: #b91c1c; }
:global(body.dark-theme) .retry-btn.success { background: #15803d; }
:global(body.dark-theme) .error-banner { background: #450a0a; border-left-color: #dc2626; color: #fecaca; }
:global(body.dark-theme) .error-content h3 { color: #fca5a5; }
</style>
