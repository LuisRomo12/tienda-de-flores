<template>
  <div class="home-view">
    <div class="hero">
      <ParticleBackground />
      <div class="hero-content">
        <h1>Bienvenido a UTFlower</h1>
        <p>Explora nuestras flores frescas y diseños exclusivos.</p>
        <router-link to="/catalogo" class="btn-primary" v-magnetic="{ strength: 0.8 }">Ver Catálogo</router-link>
      </div>
    </div>

    <!-- Nueva Sección del Carrusel Avanzado -->
    <section class="featured-carousel-section" v-scroll:up>
      <h2>Colecciones Destacadas</h2>
      <AdvancedCarousel :slides="carouselSlides" :autoplayInterval="4000" />
    </section>
  </div>
</template>

<script>
import AdvancedCarousel from '@/components/common/AdvancedCarousel.vue';
import ParticleBackground from '@/components/common/ParticleBackground.vue';

export default {
  name: 'HomeView',
  components: {
    AdvancedCarousel,
    ParticleBackground
  },
  data() {
    return {
      carouselSlides: [
        {
          id: 'slide-1',
          image: new URL('@/assets/flower-1.png', import.meta.url).href,
          title: 'Dulce Romance',
          description: 'Elegantes tulipanes en tonos rosados, perfectos para expresar cariño sincero y admiración.'
        },
        {
          id: 'slide-2',
          image: new URL('@/assets/flower-2.png', import.meta.url).href,
          title: 'Elegancia Blanca',
          description: 'Lirios blancos radiantes que simbolizan la pureza y paz, ideales para ocasiones verdaderamente especiales.'
        },
        {
          id: 'slide-3',
          image: new URL('@/assets/flower-3.png', import.meta.url).href,
          title: 'Jardín de Tulipanes',
          description: 'Refleja la alegría de la primavera con este campo de coloridos y hermosos tulipanes frescos.'
        }
      ]
    }
  }
}
</script>

<style scoped>
.home-view {
  padding: 40px 5%;
  text-align: center;
}

.hero {
  position: relative;
  width: 100%;
  min-height: 50vh; /* Para dar más espacio al efecto */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* z-index: 1 no es necesario si manejamos los hijos */
}

.hero-content {
  position: relative;
  z-index: 10;
  pointer-events: auto;
  background: var(--bg-creme); 
  opacity: 0.9;
  padding: 40px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
  box-shadow: 0 10px 30px var(--card-shadow);
  transition: background-color 0.4s ease;
}

.btn-primary {
  display: inline-block;
  background-color: #D1823C; /* Tu color ocre */
  color: white;
  padding: 10px 20px;
  text-decoration: none;
  border-radius: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(209, 130, 60, 0.3);
}

.btn-primary:hover {
  background-color: #e09249;
  transform: scale(1.05); /* Hover animado requerido en punto 3 */
  box-shadow: 0 6px 15px rgba(209, 130, 60, 0.5);
}

.featured-carousel-section {
  margin-top: 60px;
  padding: 40px 0;
}

.featured-carousel-section h2 {
  color: var(--accent-pink);
  font-size: 2.5rem;
  margin-bottom: 30px;
  font-family: 'Playfair Display', serif;
  transition: color 0.4s ease;
}
</style>