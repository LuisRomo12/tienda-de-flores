<template>
  <div class="about-container">
    <section class="about-hero" v-scroll:up>
      <h1>Nuestra Historia</h1>
      <div class="divider"></div>
      <p class="subtitle">Conectando personas a través de la belleza natural de las flores.</p>
    </section>

    <div class="content-wrapper">
      <div class="card" v-scroll:up="'100ms'">
        <div class="icon-header">🌸</div>
        <h2>¿Quiénes somos?</h2>
        <p>
          UTFLOWER nació de la pasión por llevar frescura y creatividad a cada rincón. 
          Somos una empresa dedicada a proporcionar los arreglos más hermosos para todas tus ocasiones especiales.
        </p>
      </div>

      <div class="card highlight" v-scroll:up="'300ms'">
        <h2>Nuestra Misión</h2>
        <p>
          Ofrecer productos de la más alta calidad y un servicio excepcional, 
          asegurando que cada pétalo cuente una historia de amor, amistad o gratitud.
        </p>
      </div>

      <div class="card" v-scroll:up="'500ms'">
        <h2>¿Por qué elegirnos?</h2>
        <ul class="benefit-list">
          <li>✔ Flores frescas de productores locales.</li>
          <li>✔ Diseños personalizados para cada cliente.</li>
          <li>✔ Entrega rápida y confiable.</li>
        </ul>
      </div>
    </div>

    <section class="faq-section" v-scroll:up>
      <h2>Preguntas Frecuentes</h2>
      <div class="faq-list">
        <div 
          v-for="(faq, index) in faqs" 
          :key="index"
          class="faq-item"
        >
          <button class="faq-question" @click="toggleFaq(index)">
            <span>{{ faq.question }}</span>
            <span class="faq-icon" :class="{ 'is-open': faq.isOpen }">↓</span>
          </button>
          
          <SmoothCollapse :isOpen="faq.isOpen">
            <div class="faq-answer">
              {{ faq.answer }}
            </div>
          </SmoothCollapse>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import SmoothCollapse from '@/components/common/SmoothCollapse.vue';

export default {
  name: 'AboutView',
  components: {
    SmoothCollapse
  },
  data() {
    return {
      faqs: [
        {
          question: '¿Realizan envíos a todo el país?',
          answer: 'Actualmente, nuestros envíos cubren el área metropolitana y alrededores. Estamos trabajando para expandir nuestras zonas de entrega.',
          isOpen: false
        },
        {
          question: '¿Puedo personalizar mi arreglo floral?',
          answer: 'Sí, absolutamente. Ofrecemos diseños 100% personalizados según tus preferencias de flores, colores y ocasión.',
          isOpen: false
        },
        {
          question: '¿Con cuánto tiempo de anticipación debo pedir?',
          answer: 'Recomendamos realizar tu pedido con al menos 24 horas de anticipación para asegurar la disponibilidad de las flores más frescas.',
          isOpen: false
        }
      ]
    }
  },
  methods: {
    toggleFaq(index) {
      this.faqs[index].isOpen = !this.faqs[index].isOpen;
    }
  }
}
</script>

<style scoped>
.about-container {
  background-color: #FDF9F1; /* Fondo crema de tu paleta */
  min-height: 80vh;
}

.about-hero {
  text-align: center;
  padding: 60px 20px;
}

h1 {
  color: #D26259; /* Rosa intenso */
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.divider {
  width: 60px;
  height: 4px;
  background-color: #F4B8C1; /* Rosa pastel */
  margin: 0 auto 20px;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  padding: 0 20px 60px;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(90, 74, 66, 0.05);
  border: 1px solid #F4B8C1;
}

.highlight {
  border: 2px solid #D1823C; /* Color ocre */
}

h2 {
  color: #D1823C;
  margin-bottom: 15px;
}

p {
  color: #5A4A42; /* Café suave */
  line-height: 1.6;
}

.benefit-list {
  list-style: none;
  padding: 0;
  color: #5A4A42;
}

.benefit-list li {
  margin-bottom: 10px;
}

.faq-section {
  max-width: 800px;
  margin: 0 auto 60px;
  padding: 0 20px;
}

.faq-section h2 {
  text-align: center;
  margin-bottom: 30px;
}

.faq-item {
  background: white;
  margin-bottom: 15px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(90, 74, 66, 0.05);
  border: 1px solid #F4B8C1;
  overflow: hidden;
}

.faq-question {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: transparent;
  border: none;
  font-size: 1.1rem;
  color: #D1823C;
  font-weight: bold;
  cursor: pointer;
  text-align: left;
}

.faq-icon {
  transition: transform 0.3s ease;
}

.faq-icon.is-open {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 20px 20px;
  color: #5A4A42;
  line-height: 1.6;
}
</style>

<style>
/* --- DARK MODE OVERRIDES (UNSCOPED FOR HIGHER SPECIFICITY) --- */
body.dark-theme .about-container { background-color: #121212 !important; }
body.dark-theme .about-hero h1 { color: #f8fafc !important; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }
body.dark-theme .card { background: #1e1e1e !important; border-color: #333 !important; box-shadow: 0 10px 20px rgba(255,255,255,0.02) !important; color: #f1f5f9 !important; }
body.dark-theme .highlight { border-color: #d66d81 !important; }
body.dark-theme .card h2, body.dark-theme .faq-section h2 { color: #d66d81 !important; }
body.dark-theme .card p, body.dark-theme .subtitle, body.dark-theme .benefit-list { color: #cbd5e1 !important; }
body.dark-theme .faq-item { background: #1e1e1e !important; border-color: #333 !important; }
body.dark-theme .faq-question { color: #d66d81 !important; }
body.dark-theme .faq-answer { color: #cbd5e1 !important; }
</style>