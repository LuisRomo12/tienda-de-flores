<template>
  <div class="constructor-view">
    <div class="header-titles">
      <h1>Arma tu ramo de flores 💐</h1>
      <p>Arrastra las flores al canvas para crear tu composición personalizada</p>
    </div>

    <div class="workspace">
      <!-- PANEL IZQUIERDO: CANVAS (ZONA DE DROP) -->
      <div class="canvas-panel">
        <h2 class="panel-title"><span class="dot"></span> Tu Ramo</h2>
        
        <div 
          class="drop-canvas"
          ref="dropCanvas"
          :class="{ 'is-dragover': isDragOverCanvas }"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
        >
          <!-- ENVOLTURA VISUAL (CONO O CILINDRO) -> z-index muy bajo -->
          <div class="wrapping-paper-visual" v-if="selectedPaper">
             <div class="wrap-back" :style="{ backgroundColor: selectedPaper.colorBack }"></div>
             <div class="wrap-front" :style="{ backgroundColor: selectedPaper.colorFront }"></div>
          </div>

          <!-- Mensaje Placeholder -->
          <div class="placeholder-msg" v-if="bouquet.length === 0">
            <div class="placeholder-icon">💐</div>
            <p>Arrastra flores al cono central</p>
            <span>para armar tu ramo perfecto</span>
          </div>

          <!-- Zona gravitacional (Bounding Box visible solo en drag) -->
          <div class="gravity-zone" v-show="isDragOverCanvas"></div>

          <!-- Flores Agregadas al Ramo -->
          <div 
            v-for="item in bouquet" 
            :key="item.id"
            class="bouquet-item"
            :style="{ left: `${item.x}px`, top: `${item.y}px` }"
            draggable="true"
            @dragstart="handleDragStartCanvas(item, $event)"
          >
            <!-- Simulamos la flor con Emoji o Icono SVG (Dado que no tenemos imágenes específicas guardadas aquí, usaré representaciones ricas o emojis de alta calidad para el demo de la lógica) -->
            <div class="flower-visual">
              {{ item.flower.emoji }}
            </div>
            
            <!-- Botón Eliminar (Visible en Hover) -->
            <button class="delete-btn" @click.stop="removeFlower(item.id)" title="Eliminar flor">×</button>
          </div>
        </div>

        <!-- RELLENOS Y FOLLAJE (NUEVO) -->
        <div class="fillers-wrapper">
          <div class="filler-group">
            <h3 class="subsection-title"><span class="icon-dot">🌿</span> Flores de Relleno</h3>
            <div class="horizontal-scroll-container">
              <div 
                v-for="item in fillerFlowers" 
                :key="item.id" 
                class="catalog-item mini-card"
                draggable="true"
                @dragstart="handleDragStartCatalog(item, $event)"
              >
                <div class="catalog-visual mini-visual" :style="{ backgroundColor: item.bgColor }">
                  <span class="catalog-emoji mini-emoji">{{ item.emoji }}</span>
                </div>
                <div class="catalog-info mini-info">
                  <span class="catalog-name" :title="item.name">{{ item.name }}</span>
                  <span class="catalog-price">+${{ item.price }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="filler-group">
            <h3 class="subsection-title"><span class="icon-dot">🍃</span> Follaje y Hierbas</h3>
            <div class="horizontal-scroll-container">
              <div 
                v-for="item in foliageItems" 
                :key="item.id" 
                class="catalog-item mini-card"
                draggable="true"
                @dragstart="handleDragStartCatalog(item, $event)"
              >
                <div class="catalog-visual mini-visual" :style="{ backgroundColor: item.bgColor }">
                  <span class="catalog-emoji mini-emoji">{{ item.emoji }}</span>
                </div>
                <div class="catalog-info mini-info">
                  <span class="catalog-name" :title="item.name">{{ item.name }}</span>
                  <span class="catalog-price">+${{ item.price }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- PANEL DERECHO: CATÁLOGO Y ENVOLTURA -->
      <div class="right-panels">
        <!-- CATÁLOGO DE FLORES -->
        <div class="catalog-panel mb-4">
          <h2 class="panel-title"><span class="dot icon-dot">🌸</span> FLORES DISPONIBLES</h2>
          <p class="subtitle">Arrastra las flores al ramo</p>
          
          <div class="flowers-grid">
            <div 
              v-for="flower in availableFlowers" 
              :key="flower.id" 
              class="catalog-item"
              draggable="true"
              @dragstart="handleDragStartCatalog(flower, $event)"
            >
              <!-- Pseudo-imagen o placeholder bonito -->
              <div class="catalog-visual" :style="{ backgroundColor: flower.bgColor }">
                <span class="catalog-emoji">{{ flower.emoji }}</span>
              </div>
              <div class="catalog-info">
                <span class="catalog-name">{{ flower.name }}</span>
                <span class="catalog-price">${{ flower.price }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- OPCIONES DE ENVOLTURA -->
        <div class="catalog-panel">
          <h2 class="panel-title"><span class="dot icon-dot">🎀</span> ENVOLTURA</h2>
          <p class="subtitle">Elige el estilo de tu ramo</p>
          
          <div class="papers-grid">
            <div 
              v-for="paper in availablePapers" 
              :key="paper.id"
              class="paper-item"
              :class="{ 'selected': selectedPaper && selectedPaper.id === paper.id }"
              @click="selectedPaper = paper"
            >
              <div class="paper-color-swatch" :style="{ backgroundColor: paper.colorFront }"></div>
              <div class="paper-info">
                <span class="paper-name">{{ paper.name }}</span>
                <span class="paper-price">+${{ paper.price }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PANEL INFERIOR: RESUMEN Y TOTAL -->
    <div class="summary-panel">
      <h2 class="panel-title"><span class="dot icon-dot">💐</span> Tu Ramo</h2>
      
      <div v-if="bouquet.length === 0" class="empty-summary">
        Aún no hay flores en tu ramo
      </div>
      
      <div class="summary-content" v-else>
        <!-- Opcional listado rápido: 
        <div class="summary-list">
          <span v-for="(count, name) in groupedBouquet" :key="name">
            {{ count }}x {{ name }}
          </span>
        </div> 
        -->
        <p class="summary-text">
          {{ bouquet.length }} flores seleccionadas
          <span v-if="selectedPaper">| Envoltura: {{ selectedPaper.name }} (+${{ selectedPaper.price }})</span>
        </p>
      </div>

      <div class="divider"></div>
      
      <div class="total-row">
        <span>Total</span>
        <span class="total-amount">${{ totalPrice.toFixed(2) }}</span>
      </div>
      
      <div class="action-buttons">
        <button class="btn-clear" @click="clearBouquet" :disabled="bouquet.length === 0">
          🗑️ Limpiar
        </button>
        <div class="primary-actions">
          <button class="btn-cart" :disabled="bouquet.length === 0">
            🛒 Agregar al carrito
          </button>
          <button class="btn-order" :disabled="bouquet.length === 0" @click="openConfirmModal">
            📦 Ordenar ›
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Simulado (Básico para confirmar orden) -->
    <div class="modal-overlay" v-if="showModal" @click="showModal = false">
      <div class="modal-content" @click.stop>
        <h2>¡Ramo Confirmado! 🎉</h2>
        <p>Has creado un hermoso ramo con {{ bouquet.length }} flores.</p>
        <p>Total a pagar: <strong>${{ totalPrice.toFixed(2) }}</strong></p>
        <button class="btn-primary" @click="finalizeOrder">Entendido</button>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'ConstructorView',
  data() {
    return {
      // Catálogo de 8 flores predefinidas
      availableFlowers: [
        { id: 'f1', name: 'Rosa Roja', price: 45, emoji: '🌹', bgColor: '#FFD1DC' },
        { id: 'f2', name: 'Lirio Blanco', price: 55, emoji: '⚜️', bgColor: '#E8F4F8' }, // Fleur-de-lis como Lirio
        { id: 'f3', name: 'Girasol', price: 40, emoji: '🌻', bgColor: '#FFF4CC' },
        { id: 'f4', name: 'Lavanda', price: 35, emoji: '🌿', bgColor: '#E6E6FA' },
        { id: 'f5', name: 'Tulipán Rosa', price: 50, emoji: '🌷', bgColor: '#F4B8C1' },
        { id: 'f6', name: 'Margarita', price: 25, emoji: '🌼', bgColor: '#FDF9F1' },
        { id: 'f7', name: 'Orquídea', price: 75, emoji: '💮', bgColor: '#F0E6FA' },
        { id: 'f8', name: 'Peonía', price: 65, emoji: '🌺', bgColor: '#FFB6C1' }
      ],
      // Flores de Relleno Populares
      fillerFlowers: [
        { id: 'r1', name: 'Velo de Novia (Gypsophila)', price: 15, emoji: '💮', bgColor: '#FDF9F1' },
        { id: 'r2', name: 'Statice (Lavanda Mar)', price: 18, emoji: '🪻', bgColor: '#E6E6FA' }, 
        { id: 'r3', name: 'Solidago', price: 12, emoji: '🌾', bgColor: '#FFF4CC' },
        { id: 'r4', name: 'Flor de Cera', price: 16, emoji: '🌸', bgColor: '#FFD1DC' },
        { id: 'r5', name: 'Astromelia', price: 20, emoji: '🌺', bgColor: '#F4B8C1' }
      ],
      // Follaje y Hierbas
      foliageItems: [
        { id: 'fol1', name: 'Eucalipto', price: 10, emoji: '🌿', bgColor: '#E8F4F8' },
        { id: 'fol2', name: 'Rusco', price: 12, emoji: '🍃', bgColor: '#E6F0E6' },
        { id: 'fol3', name: 'Hoja de Limonero', price: 8, emoji: '🍋', bgColor: '#FDF9F1' },
        { id: 'fol4', name: 'Romero', price: 10, emoji: '🌱', bgColor: '#E6FAEC' },
        { id: 'fol5', name: 'Menta', price: 9, emoji: '🪴', bgColor: '#EAF4E8' },
        { id: 'fol6', name: 'Salvia', price: 11, emoji: '🌿', bgColor: '#F0F4E6' }
      ],
      // Array interactivo del ramo en el canvas
      bouquet: [],
      
      // Envolturas disponibles
      availablePapers: [
        { id: 'p1', name: 'Kraft Rústico', price: 15, colorFront: '#C9A381', colorBack: '#A88464' },
        { id: 'p2', name: 'Seda Rosa', price: 20, colorFront: '#F8C8D4', colorBack: '#E3A3B4' },
        { id: 'p3', name: 'Negro Elegante', price: 25, colorFront: '#2C2C2C', colorBack: '#1A1A1A' },
        { id: 'p4', name: 'Celofán (Transparente)', price: 10, colorFront: 'rgba(255,255,255,0.4)', colorBack: 'rgba(200,200,200,0.3)' }
      ],
      selectedPaper: null, // Asignaremos por defecto en created()

      isDragOverCanvas: false,
      showModal: false,
      
      // Control interno para saber qué tipo de arrastre estamos haciendo
      draggedItemMode: null, // 'from_catalog' o 'from_canvas'
      draggedItemData: null,
      dragOffset: { x: 0, y: 0 } // Para arrastrar por el centro o click exacto
    };
  },
  computed: {
    totalPrice() {
      const flowersTotal = this.bouquet.reduce((acc, item) => acc + item.flower.price, 0);
      const paperTotal = this.selectedPaper ? this.selectedPaper.price : 0;
      return flowersTotal + paperTotal;
    },
    // Opcional para mostrar cuantas de cada una hay
    groupedBouquet() {
      const groups = {};
      this.bouquet.forEach(item => {
        if (!groups[item.flower.name]) groups[item.flower.name] = 0;
        groups[item.flower.name]++;
      });
      return groups;
    }
  },
  created() {
    // Seleccionar el Kraft por defecto
    this.selectedPaper = this.availablePapers[0];
  },
  methods: {
    // ---- DRAG DESDE EL CATÁLOGO ----
    handleDragStartCatalog(flower, event) {
      this.draggedItemMode = 'from_catalog';
      this.draggedItemData = flower;
      
      // Guardar el id genérico en el dataTransfer por estándar HTML5
      event.dataTransfer.setData('text/plain', flower.id);
      event.dataTransfer.effectAllowed = 'copy';
      
      // Calcular ofsset del ratón (aproximado, centrado en el visual)
      this.dragOffset = { x: 30, y: 30 }; 
    },

    // ---- DRAG RE-POSICIONANDO DENTRO DEL CANVAS ----
    handleDragStartCanvas(item, event) {
      this.draggedItemMode = 'from_canvas';
      this.draggedItemData = item;
      
      event.dataTransfer.setData('text/plain', item.id);
      event.dataTransfer.effectAllowed = 'move';
      
      // Capturamos el clic exacto en la flor para moverla fluidamente sin saltos
      const rect = event.target.getBoundingClientRect();
      this.dragOffset = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      };
    },

    // ---- DROP ZONE (CANVAS) ----
    handleDragOver(event) {
      this.isDragOverCanvas = true;
      event.dataTransfer.dropEffect = this.draggedItemMode === 'from_catalog' ? 'copy' : 'move';
    },

    handleDragLeave() {
      this.isDragOverCanvas = false;
    },

    handleDrop(event) {
      this.isDragOverCanvas = false;
      const canvasRect = this.$refs.dropCanvas.getBoundingClientRect();
      
      // Coordenadas relativas al contenedor Canvas
      // Ajustamos con el offset guardado al inicio del arrastre
      let rawX = event.clientX - canvasRect.left - this.dragOffset.x;
      let rawY = event.clientY - canvasRect.top - this.dragOffset.y;

      // Restringir los límites del canvas
      const canvasWidth = canvasRect.width;
      const canvasHeight = canvasRect.height;
      const maxX = canvasWidth - 60; // 60 = ancho aprox de la flor virtual
      const maxY = canvasHeight - 60;

      // ---- GRAVEDAD/SNAPPING HACIA EL RAMO ----
      // Queremos que el centro atraiga las flores a la zona del cono (aprox a la mitad arriba)
      const gravityPointX = canvasWidth / 2 - 30; // Centro horizontal
      const gravityPointY = canvasHeight / 2 - 60; // Ligeramente arriba del centro
      const gravityRadius = 150; // Radio del círculo del arreglo floral

      // Calcular distancia del soltado respecto al centro de gravedad
      const dx = rawX - gravityPointX;
      const dy = rawY - gravityPointY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      let finalX = rawX;
      let finalY = rawY;

      // Si soltó la flor demasiado lejos del "ramo", usar vectores para acercarla en banda elástica (snap)
      if (distance > gravityRadius) {
        // Normalizamos el vector y lo multiplicamos por un radio aleatorio dentro del límite para verse natural
        const angle = Math.atan2(dy, dx);
        const organicRadius = Math.random() * (gravityRadius * 0.8) + (gravityRadius * 0.2); 
        
        finalX = gravityPointX + Math.cos(angle) * organicRadius;
        finalY = gravityPointY + Math.sin(angle) * organicRadius;
      }

      // Asegurar que no rebase los límites absolutos de todos modos
      finalX = Math.max(0, Math.min(finalX, maxX));
      finalY = Math.max(0, Math.min(finalY, maxY));

      if (this.draggedItemMode === 'from_catalog') {
        // Generar un ID único (UUID simple) para la nueva flor de la pantalla
        const uniqueId = `bq_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
        
        this.bouquet.push({
          id: uniqueId,
          flower: this.draggedItemData,
          x: finalX,
          y: finalY,
          zIndex: this.bouquet.length + 1
        });
        
      } else if (this.draggedItemMode === 'from_canvas') {
        // Encontrar la flor en el array y actualizar sus coordenadas
        const index = this.bouquet.findIndex(item => item.id === this.draggedItemData.id);
        if (index !== -1) {
          this.bouquet[index].x = finalX;
          this.bouquet[index].y = finalY;
          // Subirla visualmente arriba del todo (opcional)
          this.bouquet.forEach(i => { if(i.zIndex > this.bouquet[index].zIndex) i.zIndex--; });
          this.bouquet[index].zIndex = this.bouquet.length;
        }
      }

      // Reset
      this.draggedItemMode = null;
      this.draggedItemData = null;
    },

    // ---- ACCIONES SECUNDARIAS ----
    removeFlower(id) {
      const index = this.bouquet.findIndex(item => item.id === id);
      if (index !== -1) {
        this.bouquet.splice(index, 1);
      }
    },

    clearBouquet() {
      if (confirm('¿Estás seguro de que deseas vaciar tu ramo?')) {
        this.bouquet = [];
      }
    },

    openConfirmModal() {
      this.showModal = true;
    },
    
    finalizeOrder() {
      this.showModal = false;
      this.bouquet = [];
    }
  }
}
</script>

<style scoped>
/* Estilos Globales Vista */
.constructor-view {
  background-color: var(--bg-creme, #F8EDEF); 
  min-height: calc(100vh - 80px); /* Ajustando sin Navbar */
  padding: 30px;
  font-family: 'Inter', sans-serif;
  color: var(--text-soft, #5A4A42);
  transition: background-color 0.4s ease, color 0.4s ease;
}

.header-titles {
  text-align: center;
  margin-bottom: 30px;
}

.header-titles h1 {
  color: #A32A55; /* Rosa magenta intenso del título */
  margin-bottom: 5px;
  font-family: 'Playfair Display', serif;
}

.header-titles p {
  color: #D66E8D; /* Rosa medio */
  font-size: 0.95rem;
}

.workspace {
  display: flex;
  gap: 30px;
  max-width: 1300px;
  margin: 0 auto 30px;
}

/* PANALES GENÉRICOS */
.panel-title {
  color: #A32A55;
  font-size: 1.1rem;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #D66D81;
  border-radius: 50%;
  display: inline-block;
}
.icon-dot {
  background: none;
  font-size: 1.2rem;
}

/* CANVAS (IZQUIERDA) */
.canvas-panel {
  flex: 1; /* Ocupa todo el espacio restante (unos 2/3) */
}

.drop-canvas {
  background-color: var(--card-bg, #FDF4F6); /* Fondo blanco-rosado */
  border-radius: 16px;
  min-height: 500px;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 0 40px rgba(0,0,0,0.05); /* Suavizado para dark mode */
  transition: all 0.3s ease;
  /* Fondo estilo grilla de puntos ligerita (opcional) */
  background-image: radial-gradient(var(--border-color) 1px, transparent 1px);
  background-size: 20px 20px;
}

.drop-canvas.is-dragover {
  background-color: #FFE6EA;
  border: 2px dashed #D66D81;
}

.placeholder-msg {
  position: absolute;
  top: 30%; /* Subido porque el tapel ocupará la parte inferior */
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #D66D81;
  z-index: 5;
}

/* ÁREA DE GRAVEDAD / SNAP (OCULTA HASTA QUE SE ARRASTRA) */
.gravity-zone {
  position: absolute;
  top: calc(50% - 60px);
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  border-radius: 50%;
  border: 2px dashed rgba(214, 109, 129, 0.4);
  background: radial-gradient(rgba(244, 184, 193, 0.2), transparent);
  pointer-events: none; /* No bloquear eventos de soltar del hijo */
  z-index: 10;
}

/* EFECTO VISUAL DEL PAPEL (CONO DE ENVOLTURA) */
.wrapping-paper-visual {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 250px;
  height: 280px;
  pointer-events: none;
  z-index: 1; /* El papel posterior va muy atrás */
}

.wrap-back, .wrap-front {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: background-color 0.4s ease;
}

/* Reverso de la envoltura (Boca que recibe las flores) */
.wrap-back {
  border-radius: 10% 10% 40% 40%;
  clip-path: polygon(10% 0%, 90% 0%, 60% 100%, 40% 100%);
  z-index: 1;
  box-shadow: inset 0 20px 40px rgba(0,0,0,0.1);
}

/* Frente del papel (Tapa visualmente el tallo ficticio) */
.wrap-front {
  clip-path: polygon(15% 15%, 85% 15%, 55% 100%, 45% 100%);
  z-index: 50; /* Atraviesa las flores por delante tapando la zona inferior de estas */
  opacity: 0.95;
  box-shadow: 0 -10px 20px rgba(0,0,0,0.05);
}

/* ITEM DEL RAMO EN EL CANVAS */
.bouquet-item {
  position: absolute;
  cursor: grab;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  /* Animación súper suave de soltado y de snapping elástico */
  transition: transform 0.2s, left 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), top 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 20; /* Entre la pared frontal y trasera de la envoltura */
}

.bouquet-item:active {
  cursor: grabbing;
  transform: scale(1.1);
  opacity: 0.8;
}

.flower-visual {
  font-size: 3rem; /* Tamaño de la flor en el ramo (hecha puros emojis en el demo) */
  filter: drop-shadow(0 4px 5px rgba(0,0,0,0.1));
}

.delete-btn {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 14px;
  line-height: 1;
  display: none; /* Oculto por defecto */
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.bouquet-item:hover .delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* PANELES DERECHOS CONTENEDOR */
.right-panels {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 380px;
}

/* CATÁLOGO (DERECHA Y PAPELES) */
.catalog-panel {
  background-color: var(--card-bg, white);
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 10px 30px var(--card-shadow, rgba(163, 42, 85, 0.08)); 
  transition: background-color 0.4s ease, box-shadow 0.4s ease;
}

.subtitle {
  color: #D66D81;
  font-size: 0.85rem;
  margin-bottom: 20px;
}

.flowers-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.catalog-item {
  position: relative;
  background: var(--card-bg, white);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px var(--card-shadow, rgba(0,0,0,0.05));
  cursor: grab;
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.4s ease;
  border: 1px solid var(--border-color, transparent);
}

.catalog-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(214, 109, 129, 0.2);
  border-color: #F4B8C1;
}

.catalog-visual {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.catalog-emoji {
  font-size: 4rem;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
}

.catalog-info {
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.catalog-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-soft, #5A4A42);
  margin-bottom: 4px;
}

.catalog-price {
  font-size: 0.8rem;
  color: #A32A55;
  font-weight: bold;
}

/* NUEVAS SECCIONES RELLENOS Y FOLLAJE */
.fillers-wrapper {
  margin-top: 25px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filler-group {
  background: var(--card-bg, white);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px var(--card-shadow, rgba(0,0,0,0.05));
  transition: background-color 0.4s ease, box-shadow 0.4s ease;
}

.subsection-title {
  color: var(--text-soft, #A32A55);
  font-size: 1rem;
  margin-top: 0;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.horizontal-scroll-container {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding-bottom: 15px; /* Para el scrollbar */
  scrollbar-width: thin;
  scrollbar-color: var(--primary-pink) var(--border-color);
}

.horizontal-scroll-container::-webkit-scrollbar {
  height: 8px;
}
.horizontal-scroll-container::-webkit-scrollbar-track {
  background: var(--card-bg, #f1f1f1);
  border-radius: 4px;
}
.horizontal-scroll-container::-webkit-scrollbar-thumb {
  background: var(--primary-pink, #D66D81);
  border-radius: 4px;
}

.mini-card {
  min-width: 140px;
  flex: 0 0 auto;
}

.mini-visual {
  height: 70px;
}

.mini-emoji {
  font-size: 2.5rem;
}

.mini-info {
  padding: 10px;
}

.mini-info .catalog-name {
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block; /* Para que ellipsis funcione */
}

/* OPCIONES DE ENVOLTURA GRILLA */
.papers-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.paper-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  border: 1px solid #FFE6EA;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.paper-item:hover {
  background: #FFF5F7;
  border-color: #F4B8C1;
}

.paper-item.selected {
  background: #FFE6EA;
  border: 2px solid #D66D81;
  box-shadow: 0 2px 8px rgba(214, 109, 129, 0.2);
}

.paper-color-swatch {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 15px;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.paper-info {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
}

.paper-name {
  font-size: 0.9rem;
  color: var(--text-soft, #5A4A42);
  font-weight: 500;
}

.paper-price {
  font-size: 0.85rem;
  font-weight: bold;
  color: #A32A55;
}

/* RESUMEN (PANEL INFERIOR) */
.summary-panel {
  max-width: 1300px;
  margin: 0 auto;
  background: var(--card-bg, white);
  border-radius: 16px;
  padding: 25px 35px;
  box-shadow: 0 10px 30px var(--card-shadow, rgba(163, 42, 85, 0.08));
  transition: background-color 0.4s ease, box-shadow 0.4s ease;
}

.empty-summary {
  color: #D66D81;
  font-size: 0.9rem;
  text-align: center;
  opacity: 0.7;
  padding: 20px 0;
}

.summary-content {
  margin-bottom: 15px;
}

.summary-text {
  font-size: 0.95rem;
  color: #5A4A42;
}

.divider {
  height: 1px;
  background-color: #FFE6EA;
  margin: 15px 0;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  color: #A32A55;
  font-weight: 500;
}

.total-amount {
  font-size: 1.5rem;
  font-weight: 700;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.primary-actions {
  display: flex;
  gap: 15px;
}

button {
  font-family: inherit;
  font-size: 0.95rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-clear {
  background: white;
  border: 1px solid #FFE6EA;
  color: #D66D81;
  padding: 10px 20px;
}
.btn-clear:not(:disabled):hover {
  background: #FFF5F7;
  border-color: #F4B8C1;
}

.btn-cart {
  background: white;
  border: 1px solid #F4B8C1;
  color: #A32A55;
  padding: 10px 25px;
  font-weight: 500;
}
.btn-cart:not(:disabled):hover {
  background: #FFF5F7;
}

.btn-order {
  background: #A32A55;
  border: none;
  color: white;
  padding: 10px 30px;
  font-weight: 600;
}
.btn-order:not(:disabled):hover {
  background: #8a2046;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(163, 42, 85, 0.3);
}

/* MODAL */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.modal-content {
  background: var(--card-bg, white);
  color: var(--text-soft);
  padding: 40px;
  border-radius: 16px;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}
.modal-content h2 { margin-bottom: 15px; color: #A32A55; }
.modal-content p { margin-bottom: 10px; color: #5A4A42; }
.btn-primary { 
  margin-top: 20px;
  background: #D1823C; 
  color: white; 
  border: none; 
  padding: 12px 25px; 
}
.btn-primary:hover { background: #b86e2d; }

/* RESPONSIVE */
@media (max-width: 1300px) {
  .workspace {
    flex-direction: column;
  }
  .btn-clear, .btn-cart, .btn-order {
    width: 100%;
  }
}
</style>
