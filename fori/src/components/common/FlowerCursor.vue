<template>
  <div class="cursor-container">
    <div 
      class="flower-cursor" 
      :style="cursorStyle"
      :class="{ 'is-hovering': isHovering }"
    >
      <div class="flower-cursor-inner">
        <svg width="18" height="18" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" class="flower-svg">
          <path d="M50 25C50 11.1929 38.8071 0 25 0C11.1929 0 0 11.1929 0 25C0 38.8071 11.1929 50 25 50C11.1929 50 0 61.1929 0 75C0 88.8071 11.1929 100 25 100C38.8071 100 50 88.8071 50 75C50 88.8071 61.1929 100 75 100C88.8071 100 100 88.8071 100 75C100 61.1929 88.8071 50 75 50C88.8071 50 100 38.8071 100 25C100 11.1929 88.8071 0 75 0C61.1929 0 50 11.1929 50 25Z" fill="#D26259" opacity="0.8"/>
          <circle cx="50" cy="50" r="15" fill="#FDE047"/>
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FlowerCursor',
  data() {
    return {
      x: 0,
      y: 0,
      isHovering: false
    }
  },
  computed: {
    cursorStyle() {
      // Usar translate3d en lugar de left/top para forzar la aceleración de hardware
      // y minimizar los reflows del navegador
      return {
        transform: `translate3d(${this.x}px, ${this.y}px, 0)`
      }
    }
  },
  mounted() {
    // Escuchar el movimiento del ratón
    window.addEventListener('mousemove', this.updateCursor);

    // Escuchar para elementos interactivos en el DOM que hacen que el cursor crezca (hovering)
    this.addHoverListeners();
    
    // En caso de que se creen elementos después, un MutationObserver ayudaría, 
    // pero configurando esto en app mounted cubrimos lo estático por el momento.
  },
  beforeUnmount() {
    window.removeEventListener('mousemove', this.updateCursor);
    this.removeHoverListeners();
  },
  methods: {
    updateCursor(e) {
      // Usar requestAnimationFrame para super fluidez
      requestAnimationFrame(() => {
        this.x = e.clientX;
        this.y = e.clientY;
      });
    },
    addHoverListeners() {
      // Delegación global para elementos clickeables
      document.addEventListener('mouseover', this.handleMouseOver);
      document.addEventListener('mouseout', this.handleMouseOut);
    },
    removeHoverListeners() {
      document.removeEventListener('mouseover', this.handleMouseOver);
      document.removeEventListener('mouseout', this.handleMouseOut);
    },
    handleMouseOver(e) {
      if (e.target.tagName.toLowerCase() === 'a' || 
          e.target.tagName.toLowerCase() === 'button' ||
          e.target.closest('a') !== null ||
          e.target.closest('button') !== null ||
          e.target.classList.contains('interactive-hover')
      ) {
        this.isHovering = true;
      }
    },
    handleMouseOut(e) {
      if (e.target.tagName.toLowerCase() === 'a' || 
          e.target.tagName.toLowerCase() === 'button' ||
          e.target.closest('a') !== null ||
          e.target.closest('button') !== null ||
          e.target.classList.contains('interactive-hover')
      ) {
        this.isHovering = false;
      }
    }
  }
}
</script>

<style>
/* CSS Global Necesario */
body {
  /* Ocultamos el cursor real */
  cursor: none !important;
}

/* Forzar en todos los elementos que por defecto cambian el cursor */
a, button, input, textarea, select {
  cursor: none !important;
}
</style>

<style scoped>
.cursor-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
}

.flower-cursor {
  position: absolute;
  top: 0;
  left: 0;
  width: 18px;
  height: 18px;
  pointer-events: none;
  will-change: transform;
}

.flower-cursor-inner {
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%) scale(1);
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.flower-svg {
  animation: spin 10s linear infinite;
  transition: all 0.3s ease;
}

.flower-cursor.is-hovering .flower-cursor-inner {
  transform: translate(-50%, -50%) scale(1.15); /* Crece solo un poquito */
}

.flower-cursor.is-hovering .flower-svg {
  /* Al hacer hover la flor adquiere un giro más rápido y color sólido */
  animation: spin 3s linear infinite;
}
.flower-cursor.is-hovering .flower-svg path {
  opacity: 1;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Fallback responsive: en móviles no tiene sentido el cursor personalizado */
@media (max-width: 768px) {
  .cursor-container {
    display: none;
  }
}
</style>
