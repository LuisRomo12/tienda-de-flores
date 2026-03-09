<template>
  <div class="live-notifications-container">
    <transition-group name="notification-list" tag="div" class="notifications-wrapper">
      <div 
        v-for="notification in activeNotifications" 
        :key="notification.id" 
        class="live-notification"
        :class="notification.type"
      >
        <div class="notification-icon">
          <span v-if="notification.type === 'purchase'">🛍️</span>
          <span v-else-if="notification.type === 'stock'">🌺</span>
          <span v-else>🔔</span>
        </div>
        <div class="notification-content">
          <h4>{{ notification.title }}</h4>
          <p>{{ notification.message }}</p>
          <span class="notification-time">Justo ahora</span>
        </div>
        <button class="close-btn" @click="removeNotification(notification.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'LiveNotifications',
  data() {
    return {
      activeNotifications: [],
      seenIds: new Set(), // Set para buscar duplicados en O(1)
      mockDataPool: [
        { type: 'purchase', title: 'Nueva Venta', message: 'Alguien en tu ciudad acaba de comprar un ramo de Rosas Rojas.' },
        { type: 'purchase', title: 'Nueva Venta', message: '¡Ha salido un arreglo de Tulipanes Amarillos!' },
        { type: 'stock', title: 'Restoqueo', message: 'Acaban de llegar Girasoles frescos al inventario.' },
        { type: 'info', title: 'Oferta Relámpago', message: '20% de descuento en Lirios Blancos por la próxima hora.' },
        { type: 'stock', title: 'Aviso', message: 'Quedan pocas unidades del ramo "Dulce Romance".' }
      ],
      wsSimulator: null
    }
  },
  mounted() {
    this.startMockWebSocket();
  },
  beforeUnmount() {
    if (this.wsSimulator) {
      clearInterval(this.wsSimulator);
    }
  },
  methods: {
    // 1. WebSocket Simulado o Polling inteligente
    startMockWebSocket() {
      // Usaremos setTimeout recursivo para simular un stream de eventos de tiempo variable
      const scheduleNextEvent = () => {
        // Generar un tiempo aleatorio entre 5 y 15 segundos
        const delay = Math.floor(Math.random() * 10000) + 5000;
        
        this.wsSimulator = setTimeout(() => {
          // Generar un evento "ficticio" del Mock WebSocket
          const randomItem = this.mockDataPool[Math.floor(Math.random() * this.mockDataPool.length)];
          const mockSocketEvent = {
            id: `evt-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
            ...randomItem
          };
          
          this.handleIncomingData(mockSocketEvent);
          
          // Agendar el siguiente evento (Polling inteligente / Keep-alive socket simulado)
          scheduleNextEvent();
        }, delay);
      };
      
      // Iniciar el ciclo
      scheduleNextEvent();
    },
    
    // 2. Renderizar datos, 3. Animación, 4. Prevención de Duplicados
    handleIncomingData(data) {
      // PREVENCIÓN DE DUPLICADOS IMPORTANTÍSIMA
      if (this.seenIds.has(data.id)) {
        console.warn(`[Prevención de Duplicados] Mensaje bloqueado. ID ya procesado: ${data.id}`);
        return;
      }
      
      // Registrar que ya vimos este ID
      this.seenIds.add(data.id);
      
      // Mantener control de memoria. Limpiar Set si crece mucho
      if (this.seenIds.size > 1000) {
        this.seenIds.clear();
      }
      
      // Agregar al inicio del arreglo para que aparezca arriba
      this.activeNotifications.unshift(data);
      console.log(`[WebSocket Simulado] Nuevo mensaje recibido:`, data.title);
      
      // Auto-eliminar la notificación después de 6 segundos
      setTimeout(() => {
        this.removeNotification(data.id);
      }, 6000);
      
      // Limitar a máximo 3 notificaciones visibles simultáneamente en la pantalla
      if (this.activeNotifications.length > 3) {
        this.activeNotifications.pop();
      }
    },
    
    removeNotification(id) {
      const index = this.activeNotifications.findIndex(n => n.id === id);
      if (index !== -1) {
        this.activeNotifications.splice(index, 1);
      }
    }
  }
}
</script>

<style scoped>
/* 5. Notificación Visual (Toast) Posicionamiento */
.live-notifications-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 9999;
  width: 320px;
  pointer-events: none; /* Dejar pasar clics si no le dan justo al toast */
}

.notifications-wrapper {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.live-notification {
  pointer-events: auto; /* Reactivar clics dentro del toast para el botón cerrar */
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  display: flex;
  padding: 16px;
  gap: 12px;
  border-left: 5px solid #D26259;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.live-notification.purchase { border-left-color: #D66D81; }
.live-notification.stock { border-left-color: #D1823C; }
.live-notification.info { border-left-color: #FDE047; }

.notification-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 4px 0;
  font-size: 0.95rem;
  color: #333;
}

.notification-content p {
  margin: 0 0 6px 0;
  font-size: 0.85rem;
  color: #666;
  line-height: 1.3;
}

.notification-time {
  font-size: 0.7rem;
  color: #999;
  font-style: italic;
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #999;
  cursor: pointer;
  line-height: 1;
  padding: 0 4px;
}

.close-btn:hover {
  color: #333;
}

/* ANIMACIONES DE VUE TRANSITION-GROUP */
/* Estas clases son requeridas e inyectadas por transición-group con el prefijo 'notification-list' */

.notification-list-enter-active,
.notification-list-leave-active {
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Efecto rebote */
}

.notification-list-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}

.notification-list-leave-to {
  opacity: 0;
  transform: translateY(-30px) scale(0.9);
}

/* Anima la posición de los elementos cuando otros son agregados/eliminados */
.notification-list-move {
  transition: transform 0.5s ease;
}

/* Asegurar que el elemento que sale no estropee el flujo de animación de los demás */
.notification-list-leave-active {
  position: absolute;
  width: calc(100% - 32px); /* Mantener ancho (padding lateral) para el layout slide */
}

@media (max-width: 480px) {
  .live-notifications-container {
    bottom: 20px;
    right: 20px;
    left: 20px;
    width: auto;
  }
}
</style>
