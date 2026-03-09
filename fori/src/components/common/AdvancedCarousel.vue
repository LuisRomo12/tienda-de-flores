<template>
  <div 
    class="advanced-carousel"
    @mouseenter="pauseAutoplay"
    @mouseleave="startAutoplay"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
  >
    <div class="carousel-track-wrapper">
      <div 
        class="carousel-track"
        :style="trackStyle"
        @transitionend="handleTransitionEnd"
      >
        <!-- Slides originales (con clones al principio y al final para el bucle simulado) -->
        <div 
          v-for="(slide, index) in extendedSlides" 
          :key="`${index}-${slide.id}`"
          class="carousel-slide"
        >
          <img :src="slide.image" :alt="slide.title" draggable="false"/>
          <div class="slide-content">
            <h3>{{ slide.title }}</h3>
            <p>{{ slide.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Controles Manuales -->
    <button class="carousel-btn prev-btn" @click="prevSlide" aria-label="Anterior">
      &#10094;
    </button>
    <button class="carousel-btn next-btn" @click="nextSlide" aria-label="Siguiente">
      &#10095;
    </button>

    <!-- Indicadores Dinámicos -->
    <div class="carousel-indicators">
      <button 
        v-for="(_, index) in slides" 
        :key="`indicator-${index}`"
        class="indicator-dot"
        :class="{ active: currentRealIndex === index }"
        @click="goToSlide(index)"
        :aria-label="`Ir a la diapositiva ${index + 1}`"
      ></button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdvancedCarousel',
  props: {
    slides: {
      type: Array,
      required: true
    },
    autoplayInterval: {
      type: Number,
      default: 5000
    }
  },
  data() {
    return {
      currentIndex: 1, // Empieza en 1 porque el 0 es el clon del final
      isTransitioning: false,
      autoplayTimer: null,
      
      // Touch events data
      touchStartX: 0,
      touchEndX: 0,
      currentTouchX: 0,
      isDragging: false,
      swipeThreshold: 50
    }
  },
  computed: {
    // Array con clones para el loop infinito simulado
    extendedSlides() {
      if (this.slides.length === 0) return [];
      
      const firstClone = { ...this.slides[0], id: 'clone-first' };
      const lastClone = { ...this.slides[this.slides.length - 1], id: 'clone-last' };
      
      return [lastClone, ...this.slides, firstClone];
    },
    
    trackStyle() {
      // Cálculo del arrastre táctil (drag) en tiempo real
      let dragOffset = 0;
      if (this.isDragging) {
        // En lugar de px, lo convertiremos aproximadamente a % de viewport para css
        dragOffset = ((this.currentTouchX - this.touchStartX) / window.innerWidth) * 100;
      }
      
      return {
        // Combinamos la posición de la diapositiva actual con el arrastre del dedo
        transform: `translateX(calc(-${this.currentIndex * 100}% + ${dragOffset}%))`,
        // Quitamos la transición *mientras* el dedo está arrastrando para que sea instantáneo 1:1
        transition: this.isTransitioning && !this.isDragging ? 'transform 0.5s ease-in-out' : 'none'
      }
    },
    
    // Índice real (0-based) ignorando clones para los indicadores
    currentRealIndex() {
      if (this.currentIndex === 0) return this.slides.length - 1;
      if (this.currentIndex === this.slides.length + 1) return 0;
      return this.currentIndex - 1;
    }
  },
  mounted() {
    this.startAutoplay();
  },
  beforeUnmount() {
    this.pauseAutoplay();
  },
  methods: {
    nextSlide() {
      if (this.isTransitioning) return;
      this.isTransitioning = true;
      this.currentIndex++;
    },
    
    prevSlide() {
      if (this.isTransitioning) return;
      this.isTransitioning = true;
      this.currentIndex--;
    },
    
    goToSlide(realIndex) {
      if (this.isTransitioning) return;
      this.isTransitioning = true;
      // Ajustamos por el offset del clon inicial
      this.currentIndex = realIndex + 1;
    },
    
    handleTransitionEnd() {
      this.isTransitioning = false;
      
      // Bucle infinito simulado "sin costuras"
      if (this.currentIndex === 0) {
        // Hemos retrocedido más allá del primero (estamos en el clon del último)
        // Saltamos instantáneamente (sin transición) al último real
        this.currentIndex = this.slides.length;
      } else if (this.currentIndex === this.extendedSlides.length - 1) {
        // Hemos avanzado más allá del último (estamos en el clon del primero)
        // Saltamos instantáneamente al primero real
        this.currentIndex = 1;
      }
    },
    
    startAutoplay() {
      if (!this.autoplayTimer) {
        this.autoplayTimer = setInterval(() => {
          this.nextSlide();
        }, this.autoplayInterval);
      }
    },
    
    pauseAutoplay() {
      if (this.autoplayTimer) {
        clearInterval(this.autoplayTimer);
        this.autoplayTimer = null;
      }
    },
    
    // Soportes Táctiles (Touch Events)
    handleTouchStart(e) {
      if (this.isTransitioning && !this.isDragging) return;
      this.pauseAutoplay();
      this.isDragging = true;
      this.touchStartX = e.touches ? e.touches[0].screenX : e.screenX; // Soporte táctil y ratón (emulado)
      this.currentTouchX = this.touchStartX;
    },
    handleTouchMove(e) {
      if (!this.isDragging) return;
      // Implementación del arrastre en tiempo real actualizando la posición
      this.currentTouchX = e.touches ? e.touches[0].screenX : e.screenX;
    },
    handleTouchEnd(e) {
      if (!this.isDragging) return;
      this.isDragging = false;
      this.touchEndX = e.changedTouches ? e.changedTouches[0].screenX : e.screenX;
      this.handleSwipeGesture();
      this.startAutoplay();
    },
    handleSwipeGesture() {
      const difference = this.touchStartX - this.touchEndX;
      
      // La transición se reactiva al llamar nextSlide/prevSlide
      if (Math.abs(difference) > this.swipeThreshold) {
        if (difference > 0) {
          // Deslizó hacia la izquierda (Siguiente)
          this.nextSlide();
        } else {
          // Deslizó hacia la derecha (Anterior)
          this.prevSlide();
        }
      } else {
        // Si no pasó el umbral, forzamos la reactivación de transición 
        // para que "vuelva" (snap) elásticamente a su sitio sin cambiar de slide
        this.isTransitioning = true; 
        
        // Un reflow rápido forzado para aplicar la transición de regreso instantáneamente
        setTimeout(() => this.isTransitioning = false, 500);
      }
    }
  }
}
</script>

<style scoped>
.advanced-carousel {
  position: relative;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  overflow: hidden;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(90, 74, 66, 0.15);
  background: var(--bg-creme, #FDF9F1);
}

.carousel-track-wrapper {
  overflow: hidden;
  width: 100%;
}

.carousel-track {
  display: flex;
  width: 100%;
  /* will-change optimiza la aceleración del hardware durante las transiciones */
  will-change: transform; 
}

.carousel-slide {
  /* Flex basis asegura que tome el 100% exacto de la vista para un deslizamiento fluido */
  flex: 0 0 100%;
  position: relative;
}

.carousel-slide img {
  width: 100%;
  height: 500px;
  object-fit: cover;
  display: block;
}

.slide-content {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 40px 30px 30px;
  background: linear-gradient(to top, rgba(90, 74, 66, 0.8), transparent);
  color: white;
  text-align: left;
}

.slide-content h3 {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #F4B8C1;
}

.slide-content p {
  font-size: 1.1rem;
}

/* Controles manuales */
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.7);
  color: #D1823C;
  border: none;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-btn:hover {
  background: white;
  color: #D66D81;
  transform: translateY(-50%) scale(1.1); /* Efecto en punto 3 aplicado aquí tmb */
}

.prev-btn { left: 20px; }
.next-btn { right: 20px; }

/* Indicadores dinámicos */
.carousel-indicators {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 10;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.indicator-dot:hover {
  background: rgba(255, 255, 255, 0.8);
}

.indicator-dot.active {
  background: #D1823C;
  transform: scale(1.3);
  width: 20px;
  border-radius: 6px;
}

@media (max-width: 768px) {
  .carousel-slide img { height: 350px; }
  .slide-content h3 { font-size: 1.5rem; }
  .carousel-btn { width: 40px; height: 40px; font-size: 1.2rem; }
}
</style>
