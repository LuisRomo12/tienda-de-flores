<template>
  <div 
    class="smooth-collapse" 
    :style="wrapperStyle"
    @transitionend="onTransitionEnd"
  >
    <div ref="collapseContent" class="collapse-content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SmoothCollapse',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      currentHeight: '0px',
      isAnimating: false
    }
  },
  computed: {
    wrapperStyle() {
      return {
        height: this.currentHeight,
        opacity: this.isOpen ? 1 : 0,
        transform: this.isOpen ? 'translateY(0)' : 'translateY(-10px)',
        pointerEvents: this.isOpen ? 'auto' : 'none',
        overflow: 'hidden' // Ocultamos el scroll/contenido sobrante mientras la altura es menor o estamos cerrados
      }
    }
  },
  watch: {
    isOpen(newVal) {
      this.isAnimating = true;
      if (newVal) {
        // Al abrir, primero establecemos auto momentáneamente (invisible) si queremos saber la altura, 
        // pero con scrollHeight lo obtenemos de todos modos del inner container.
        const height = this.$refs.collapseContent.scrollHeight;
        this.currentHeight = `${height}px`;
      } else {
        // Al cerrar, si estamos en 'auto', fijamos a px explícitos un tick antes
        this.currentHeight = `${this.$refs.collapseContent.scrollHeight}px`;
        
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            this.currentHeight = '0px';
          });
        });
      }
    }
  },
  mounted() {
    // Estado inicial
    if (this.isOpen) {
      this.currentHeight = 'auto';
    } else {
      this.currentHeight = '0px';
    }
  },
  methods: {
    onTransitionEnd(event) {
      // Solo nos importa si terminó la altura y fue para abrir
      if (event.propertyName === 'height') {
        this.isAnimating = false;
        if (this.isOpen) {
          // Dejar en auto para que el contenido sea flexible (ej. redimensionar ventana)
          this.currentHeight = 'auto';
        }
      }
    }
  }
}
</script>

<style scoped>
.smooth-collapse {
  transition: height 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), 
              opacity 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), 
              transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  will-change: height, opacity, transform;
}
.collapse-content {
  padding: 0.1px 0; /* Anti margin collapse */
}
</style>
