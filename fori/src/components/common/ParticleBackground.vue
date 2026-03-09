<template>
  <div class="particle-container" ref="container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script>
export default {
  name: 'ParticleBackground',
  data() {
    return {
      particles: [],
      ctx: null,
      animationFrameId: null,
      mouse: {
        x: null,
        y: null,
        radius: 120 // Radio de repulsión del mouse
      },
      colors: ['#D26259', '#F4B8C1', '#D1823C', '#FDE047', '#5A4A42']
    }
  },
  mounted() {
    this.initCanvas();
    this.throttledResize = this.throttle(this.handleResize, 250);
    window.addEventListener('resize', this.throttledResize);
    window.addEventListener('mousemove', this.handleMouseMove);
    window.addEventListener('mouseout', this.handleMouseOut);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.throttledResize);
    window.removeEventListener('mousemove', this.handleMouseMove);
    window.removeEventListener('mouseout', this.handleMouseOut);
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  },
  methods: {
    throttle(func, limit) {
      let inThrottle;
      return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
          func.apply(context, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      }
    },
    
    initCanvas() {
      const canvas = this.$refs.canvas;
      const container = this.$refs.container;
      
      canvas.width = container.offsetWidth;
      canvas.height = container.offsetHeight;
      this.ctx = canvas.getContext('2d');
      
      this.createParticles();
      this.animate();
    },
    
    handleResize() {
      const canvas = this.$refs.canvas;
      const container = this.$refs.container;
      canvas.width = container.offsetWidth;
      canvas.height = container.offsetHeight;
      this.createParticles();
    },
    
    handleMouseMove(e) {
      const containerRect = this.$refs.container.getBoundingClientRect();
      this.mouse.x = e.clientX - containerRect.left;
      this.mouse.y = e.clientY - containerRect.top;
    },
    
    handleMouseOut() {
      this.mouse.x = null;
      this.mouse.y = null;
    },
    
    createParticles() {
      this.particles = [];
      const canvas = this.$refs.canvas;
      // Cantidad de partículas basada en el tamaño de la pantalla
      const numberOfParticles = (canvas.width * canvas.height) / 7000;
      
      for (let i = 0; i < numberOfParticles; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        this.particles.push(new Particle(x, y, this.colors, canvas));
      }
    },
    
    animate() {
      this.ctx.clearRect(0, 0, this.$refs.canvas.width, this.$refs.canvas.height);
      
      for (let i = 0; i < this.particles.length; i++) {
        this.particles[i].update(this.mouse);
        this.particles[i].draw(this.ctx);
      }
      
      // Uso de requestAnimationFrame para optimizar el rendimiento de la animación.
      // A diferencia de setInterval, esto sincroniza el renderizado con la tasa de refresco 
      // del monitor (usualmente 60fps) y pausa la animación si la pestaña no está visible.
      this.animationFrameId = requestAnimationFrame(() => this.animate());
    }
  }
}

class Particle {
  constructor(x, y, colors, canvas) {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.baseX = x;
    this.baseY = y;
    this.size = Math.random() * 3 + 1;
    this.density = (Math.random() * 30) + 1;
    this.color = colors[Math.floor(Math.random() * colors.length)];
    
    // Convertir partículas en pequeños trazos/pétalos aleatorios en lugar de círculos perfectos
    this.angle = Math.random() * Math.PI * 2;
  }

  draw(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.angle);
    ctx.fillStyle = this.color;
    ctx.beginPath();
    // Dibujamos como pequeños óvalos/pétalos elongados (similar a las gotas/trazos de Antigravity)
    ctx.ellipse(0, 0, this.size * 1.5, this.size * 0.5, 0, 0, Math.PI * 2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  update(mouse) {
    // Lógica flotante suave (movimiento autónomo)
    this.angle += 0.01;
    
    let dx = mouse.x - this.x;
    let dy = mouse.y - this.y;
    let distance = Math.sqrt(dx * dx + dy * dy);
    
    // Fuerza de repulsión del mouse
    let forceDirectionX = dx / distance;
    let forceDirectionY = dy / distance;
    let maxDistance = mouse.radius;
    let force = (maxDistance - distance) / maxDistance;
    let directionX = forceDirectionX * force * this.density;
    let directionY = forceDirectionY * force * this.density;

    if (distance < mouse.radius && mouse.x !== null) {
      this.x -= directionX;
      this.y -= directionY;
    } else {
      // Retornar a la posición original suavemente
      if (this.x !== this.baseX) {
        let dx = this.x - this.baseX;
        this.x -= dx / 20;
      }
      if (this.y !== this.baseY) {
        let dy = this.y - this.baseY;
        this.y -= dy / 20;
      }
    }
  }
}
</script>

<style scoped>
.particle-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* Asegurarse de que esté detrás del contenido */
  overflow: hidden;
  pointer-events: none; /* No bloquear clics en los botones encima */
}

canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
