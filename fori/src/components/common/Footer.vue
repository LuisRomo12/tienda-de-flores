<template>
  <footer class="main-footer">
    <div class="footer-container">
      <div class="footer-brand">
        <h2 class="logo">UT<span class="accent">FLOWER</span></h2>
        <p>Llevando frescura y creatividad a cada rincón.</p>
      </div>

      <div class="footer-links">
        <h3>Explorar</h3>
        <ul>
          <li><router-link to="/catalogo">Catálogo</router-link></li>
          <li><router-link to="/constructor">Hazlo tú mismo</router-link></li>
          <li><router-link to="/nosotros">Nosotros</router-link></li>
        </ul>
      </div>

      <div class="footer-contact">
        <h3>Soporte</h3>
        <ul>
          <li><router-link to="/contacto">Contáctanos</router-link></li>
          <li><router-link to="/ayuda">Centro de Ayuda</router-link></li>
          <li><router-link to="/mapa-del-sitio">Mapa del Sitio</router-link></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
    </div>
  </footer>
</template>

<style scoped>
.main-footer {
  background-color: #FDF9F1; /* Crema de tu paleta */
  border-top: 2px solid #F4B8C1; /* Rosa pastel */
  padding: 40px 0 20px;
  color: #5A4A42; /* Café suave */
  margin-top: 50px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  padding: 0 5%;
}

.logo {
  font-size: 1.5rem;
  margin-bottom: 15px;
}

.logo .accent { color: #D1823C; } /* Ocre */

h3 {
  color: #D26259; /* Rosa intenso */
  margin-bottom: 15px;
  font-size: 1.1rem;
}

ul { list-style: none; padding: 0; }

ul li { margin-bottom: 10px; }

ul li a {
  text-decoration: none;
  color: #5A4A42;
  transition: color 0.3s;
}

ul li a:hover { color: #B7B16B; } /* Verde oliva */

.footer-bottom {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #F4B8C1;
  font-size: 0.8rem;
}
</style>