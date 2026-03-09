<template>
  <div class="error-container">
    <div class="error-content">
      <span class="error-code">404</span>
      <h1>¡Oh no! Esta flor no ha crecido aquí</h1>
      <p>Parece que la página que buscas se ha marchitado o nunca existió.</p>
      
      <router-link to="/" class="btn-back">
        Regresar al Jardín Principal
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.error-container {
  height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #FDF9F1; /* Crema de tu paleta */
  text-align: center;
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: #F4B8C1; /* Rosa pastel */
  display: block;
}

h1 { color: #D26259; margin-bottom: 1rem; } /* Rosa intenso */

p { color: #5A4A42; margin-bottom: 2rem; } /* Café suave */

.btn-back {
  background-color: #D1823C; /* Ocre */
  color: white;
  padding: 12px 25px;
  border-radius: 30px;
  text-decoration: none;
  transition: background 0.3s;
}

.btn-back:hover { background-color: #B7B16B; } /* Verde oliva */
</style>